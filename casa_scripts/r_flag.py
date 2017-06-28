import sys
import yaml


def load(config_file_name):
    config_file = open(config_file_name)
    configs = yaml.load(config_file)
    config_file.close()
    return configs

config_path = sys.argv[-1]
source_type = sys.argv[-2]
ms_dataset = sys.argv[-3]
AUTO_FLAGGING_CONFIGS = load(config_path +"auto_flagging_config.yml")
SOURCE_AUTOFLAGGING_CONFIGS = AUTO_FLAGGING_CONFIGS[source_type]['auto_flagging_algo']
config = load(config_path + "/config.yml")
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
    timedevscale = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['rflag']['timedevscale']
    freqdevscale = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['rflag']['freqdevscale']
    freqrange = SOURCE_AUTOFLAGGING_CONFIGS[spw_config]['freqrange']

    spw_with_freq = "{0}:{1}".format(spw, freqrange)
    fields = ",".join(map(str, SOURCE_CONFIG["fields"]))

    r_flag_command = "mode='rflag' extendflags=False timedevscale={0} " \
                     "freqdevscale={1}  spw='{2}' datacolumn='{3}' field='{4}' ".format(timedevscale, freqdevscale,
                                                                                        spw_with_freq,
                                                                                        datacolumn, fields)

    extend_flag_command = "mode='extend' growaround=True flagnearfreq=True flagneartime=True" \
                          " extendpols=False growtime={0} growfreq={1}  spw='{2}' datacolumn='{3}' " \
                          "field='{4}'".format(growtime, growfreq, spw, datacolumn, fields)

    cmdlist = [r_flag_command, extend_flag_command]

    flagdata(vis=ms_dataset, mode='list', inpfile=cmdlist, action='apply')
