import sys
import yaml


def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs

spw_range = sys.argv[-1]
config_path = sys.argv[-2]
source_type = sys.argv[-3]
ms_dataset = sys.argv[-4]

AUTO_FLAGGING_CONFIGS = load(config_path + "auto_flagging_config.yml")
SOURCE_AUTOFLAGGING_CONFIGS = AUTO_FLAGGING_CONFIGS[source_type]['auto_flagging_algo']
config = load(config_path + "pipeline.yml")
if source_type == "bandpass_calibrator":
    fields = config['global']['bandpass_cal_fields']
else:
    fields = config['global']['target_src_field']

for spw in spw_range.split(','):
    spw_config = "spw{0}".format(spw)
    tfcrop_config = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]
    datacolumn = tfcrop_config['datacolumn']
    growtime = tfcrop_config['growtime']
    growfreq = tfcrop_config['growfreq']
    timecutoff = tfcrop_config['tfcrop']['timecutoff']
    freqcutoff = tfcrop_config['tfcrop']['freqcutoff']
    maxnpieces = tfcrop_config['tfcrop']['maxnpieces']
    usewindowstats = tfcrop_config['tfcrop']['usewindowstats']
    halfwin = tfcrop_config['tfcrop']['halfwin']
    freqrange = tfcrop_config['freqrange']

    spw_with_freq = "{0}:{1}".format(spw, freqrange)
    fields_str = ",".join(map(str, fields))

    tfcrop_command = "mode='tfcrop' extendflags=False maxnpieces={0} usewindowstats='{1}' halfwin={2} timecutoff={3}" \
                     " freqcutoff={4}  spw='{5}' datacolumn={6} field='{7}'".format(maxnpieces, usewindowstats, halfwin,
                                                                                    timecutoff,
                                                                                    freqcutoff,
                                                                                    spw_with_freq, datacolumn, fields_str)

    extend_flag_command = "mode='extend' growaround=False flagnearfreq=False flagneartime=False" \
                          " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                          "field='{4}'".format(growtime, growfreq, spw, datacolumn, fields_str)

    cmdlist = [tfcrop_command, extend_flag_command]

    flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply')
