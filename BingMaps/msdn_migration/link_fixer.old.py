from pandas import read_csv
import sys
import yaml
from collections import namedtuple, defaultdict
import re
from pathlib import Path

'''
`ErrorData`:
- `dest_file`: The path to the file with links that need to be updated
- `service_dir`: The service directory name for the *link* that needs to be updated, e.g. `rest-services`
- `md_file`: The filename used to get link data from the YAML data file
- `old_link`: The original link
- `new_link`: the replaced link
'''

def print_log(string):
    with open('linker_log.txt', 'a') as f:
        f.write(string)

print_old = print
print = print_log

ErrorData = namedtuple('ErrorData', 'dest_file service_dir md_file old_link new_link') 

def print_error_data(error_data):
    print(f'Error Data:\
    \n\tdestination file:\t{error_data.dest_file}\
    \n\tservice dir:\t\t{error_data.service_dir}\
    \n\tmd file:\t\t{error_data.md_file}\
    \n\told link:\t\t{error_data.old_link}\
    \n\tnew link:\t\t{error_data.new_link}\n\n')


def parse_msg(msg):
    '''Parse data from OBS report'''
    # objs = re.match(r'Invalid file link:\(\~\/([-\w]+)\/([-\w]+\/)([-\w]+)\.md\).', msg)
    obj = msg.split(':(')[1].split(').')[0] # re.match(r'Invalid file link:\(\~\/([\.-\w]+)\)', msg)
    objs = obj.split('/')
    print(f"\n\tMSG: {msg}\n\tOBJ: {str(objs if objs else 'NaN')}\n")

    if objs:
        return objs[1], objs[-1]
    return None

def fit_array(array, _max):
    n = len(array)
    assert(n <= _max)
    l = []
    for i in range(_max):
        if i < n:
            l.append(array[i])
        else:
            l.append(None)
    return l[0:_max-1]

'''
def get_link_depth(dest_link, new_link):
    dest_glob = list(dest_link.split('/'))
    new_glob = list(new_link.split('/'))
    n = len(dest_glob)
    m = len(new_glob)
    size = max(n, m)

    dest_order = fit_array(dest_glob, size)
    new_order = fit_array(new_glob, size)

    index = 0
    for i in range(size - 1): # don't count filename
        if dest_order[i] == new_glob[i] and dest_order[i] and new_glob[i]:
            index += 1
    return max(0, m - index)
        
def get_link_service_level_depth(dest_link, service):
    dest_glob = list(dest_link.split('/'))
    dest_glob.reverse()
    N = len(dest_glob)
    for i, l in enumerate(dest_glob):
        if l == service:
            return i
    return N - 1
'''

def get_depth(dest_link, service_dir):
    dest_glob = list(dest_link.split('/'))
    index = 0
    dest_glob.reverse()
    for dir in dest_glob:
        if dir == service_dir:
            break
        index += 1
    print("depth for {0}, looking for {1}: {2}\n".format(dest_glob, service_dir, index - 1))

    return index - 1
        

def get_updated_filename(link_data, service, old_md_file):
    for serv in link_data:
        if serv.get('path') == service:
            for link_dict in serv.get('links'):
                if link_dict['old-docs'] == old_md_file:
                    return link_dict['new-docs'].split('/')[-1]
    return old_md_file

    
def check_extension(file_name, ext):
    return file_name.split('.')[-1] == ext

    
def get_error_data(df, link_data):
    '''
    Prepares doc data from OBS report and YAML link mapper file
    into `ErrorData` objects to be used to replace links in repo

    - `df` is a Pandas dataframe of OBS linking error info
    - `link_data` is a dict from the YAML link data file
    '''

    for [file, msg] in df[['File','Message']].values:
        print(f'\nunparsing: "{file} -- {msg}"\n')
        parse_data = parse_msg(msg)
        if parse_data and check_extension(file, 'md'):
            
            service_dir, md_file = parse_data

            old_link = f'../{service_dir}/{md_file}'           
            
            dest_file = file.replace('BingMaps', '..')
            
            for service in link_data:
                if service.get('path') == service_dir:
                    # same directory
                    for link_dict in service.get('links'):
                        
                        if link_dict['old-docs'].strip(" ") == md_file.strip(" "):

                            new_link_file = link_dict.get('new-docs')

                            if new_link_file:

                                dest_file_parts = dest_file.split('/')
                                n = len(dest_file_parts)
                                print(f"Dest file part: {dest_file_parts}\n")
                                origin_md_file = get_updated_filename(link_data, service_dir, dest_file_parts[-1])
                                print(f'new dest md filename: {origin_md_file}\n')
                                dest_file_parts[n-1] = origin_md_file
                                dest_file = str.join('/', dest_file_parts)

                                # depth = get_link_depth(dest_file, f'../{service_dir}/{new_link_file}')
                                
                                # depth = get_link_service_level_depth(dest_file, service_dir)

                                depth = get_depth(dest_file, service_dir)

                                rel_path = str.join('/', ['..' for _ in range(depth)]) + '/' if depth > 0 else '' 
                                
                                new_link = f'{rel_path}{new_link_file}' #  if depth > 0 else new_link_file.split('/')[-1]
                                
                                datum = ErrorData(dest_file, service_dir, md_file, old_link, new_link)
                                print_error_data(datum)
                                yield datum
                                break
                            else:
                                print(f"************* no new file: {md_file}\n\n.")


def update_file(error_object):
    print_error_data(error_object)
    file_name = str(Path(error_object.dest_file).absolute())
    file_str = None
    with open(file_name, 'r', encoding='utf8') as f:
        file_str = f.read()
    file_old = file_str
    file_str = file_str.replace(error_object.old_link, error_object.new_link)
    if file_str != None and file_str != file_old:
        with open(file_name, 'w', encoding='utf8') as f:
            f.write(file_str)
            print(f'Changed file "{error_object.dest_file}":\n\t"{error_object.old_link}"\n\t--> "{error_object.new_link}"\n')


'''
def relink_repo(error_data):
    for datum in error_data:
        # get write access to file to change
        file_as_string = None
        with open(get_dest_file_path(data.dist_file), 'w') as dest_f:
            file_as_string = dest_f.read()
            file_as_string.replace(
'''     


if __name__=='__main__':
    print('\nLoading link fixer, usage:\n\n\t$> link_fixer {csv_report_file} {yaml_link_file}\n')
    
    yaml_links = None
    excel_filename = None
    if len(sys.argv) > 2:
        excel_filename = sys.argv[1]
        with open(sys.argv[2], 'r') as f:
            yaml_links = yaml.load(f)
    else:
        exit(1)


    df = None
    if excel_filename:
        df = read_csv(excel_filename, sep=',')

    for err_fix in get_error_data(df, yaml_links):
        print(f'\t ---> {err_fix}\n')
        update_file(err_fix)