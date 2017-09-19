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
AUTO_FLAGGING_CONFIGS = load(config_path +"auto_flagging_config.yml")
SOURCE_AUTOFLAGGING_CONFIGS = AUTO_FLAGGING_CONFIGS[source_type]['auto_flagging_algo']
config = load(config_path + "pipeline.yml")
if source_type == "bandpass_calibrator":
    fields = config['global']['bandpass_cal_fields']
else:
    fields = config['global']['target_src_field']

for spw in spw_range.split(','):
    spw_config = "spw{0}".format(spw)
    datacolumn = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['datacolumn']
    growtime = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['growtime']
    growfreq = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['growfreq']
    timedevscale = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['rflag']['timedevscale']
    freqdevscale = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['rflag']['freqdevscale']
    freqrange = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['freqrange']

    spw_with_freq = "{0}:{1}".format(spw, freqrange)
    fields_str = ",".join(map(str, fields))

    r_flag_command = "mode='rflag' extendflags=False timedevscale={0} " \
                     "freqdevscale={1}  spw='{2}' datacolumn='{3}' field='{4}' ".format(timedevscale, freqdevscale,
                                                                                        spw_with_freq,
                                                                                        datacolumn, fields_str)

    extend_flag_command = "mode='extend' growaround=True flagnearfreq=True flagneartime=True" \
                          " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                          "field='{4}'".format(growtime, growfreq, spw, datacolumn, fields_str)
    cmdlist = [r_flag_command, extend_flag_command]

    flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply')
