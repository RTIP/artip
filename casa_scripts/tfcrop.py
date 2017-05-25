import sys
import yaml


def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs


source_type = sys.argv[-1]
ms_dataset = sys.argv[-2]
AUTO_FLAGGING_CONFIGS = load("conf/auto_flagging_config.yml")
SOURCE_AUTOFLAGGING_CONFIGS = AUTO_FLAGGING_CONFIGS[source_type]['auto_flagging_algo']
config = load("conf/config.yml")
GLOBAL_CONFIG = config["global"]
if source_type == "bandpass_calibrator":
    SOURCE_CONFIG = config[source_type]
else:
    SOURCE_CONFIG = config['target_source'][source_type]

spw_list = GLOBAL_CONFIG['spw_range']
for spw in spw_list.split(','):
    spw_config = "spw{0}".format(spw)
    datacolumn = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['datacolumn']
    growtime = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['growtime']
    growfreq = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['growfreq']
    timecutoff = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['tfcrop']['timecutoff']
    freqcutoff = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['tfcrop']['freqcutoff']
    maxnpieces = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['tfcrop']['maxnpieces']
    usewindowstats = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['tfcrop']['usewindowstats']
    halfwin = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['tfcrop']['halfwin']
    freqrange = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['freqrange']

    spw_with_freq = "{0}:{1}".format(spw, freqrange)
    fields = ",".join(map(str, SOURCE_CONFIG["fields"]))

    tfcrop_command = "mode='tfcrop' extendflags=False maxnpieces={0} usewindowstats='{1}' halfwin={2} timecutoff={3}" \
                     " freqcutoff={4}  spw='{5}' datacolumn={6} field='{7}'".format(maxnpieces, usewindowstats, halfwin,
                                                                                    timecutoff,
                                                                                    freqcutoff,
                                                                                    spw_with_freq, datacolumn, fields)

    extend_flag_command = "mode='extend' growaround=False flagnearfreq=False flagneartime=False" \
                          " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                          "field='{4}'".format(growtime, growfreq, spw, datacolumn, fields)

    cmdlist = [tfcrop_command, extend_flag_command]

    flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply')
