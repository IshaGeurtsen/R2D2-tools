#! python
import configparser

def generate_commit_list_config(config_file):
    config = configparser.ConfigParser()

    commit_list_section = 'commit_list'
    config.add_section(commit_list_section)
    config[commit_list_section]['apikey'] = ''
    config[commit_list_section]['username'] = ''
    config.write(config_file)


if __name__ == "__main__":
    with open('config.ini', 'w') as config_file:
        generate_commit_list_config(config_file)
