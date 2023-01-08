#!/usr/bin/python3
'''
'''
import os
import sys
import json
import gzip
#import zipfile
import time
import copy
import argparse
import pathlib
from tabulate import tabulate

t_start = time.perf_counter()
d = None
data = None
def update_totals(data: dict):
    # Delete exiting total
    totals_key="--- blob-totals ---"
    t={'cnt':0, 'bytes': 0, 'bytes_max': 0, 'bytes_min':-1, 'cnt_zerobyte': 0 }
    for k,v in data.items():
        if k == totals_key: continue #Dont add previous total to total
        t['cnt']=t['cnt']+v['cnt']
        t['bytes']=t['bytes']+v['bytes']
        t['bytes_max']=t['bytes_max'] if t['bytes_max'] > v['bytes_max'] else v['bytes_max']
        t['bytes_min']=t['bytes_min'] if t['bytes_min'] > -1 and t['bytes_min'] < v['bytes_min'] else v['bytes_min']
        t['cnt_zerobyte']=t['cnt_zerobyte']+v['cnt_zerobyte']
    data[totals_key]=t


def pprint(data: dict(), tablefmt='jira', stream=sys.stdout):
    # sorted change dict("<container>: { <data fields> }") into list[ (<container>, <data fields>)]
    update_totals(data) #Add blob-totals
    data_sorted=sorted(copy.deepcopy(data).items(), key=lambda x: x[1]['bytes'])
    #print(f"{data_sorted[0]=}", file=stream)
    # update with calculated fields.
    for entry in data_sorted:
        k = entry[0]
        v = entry[1]
        v['cnt']     = f"{v['cnt']:,}"
        v['bytesGB'] = f"{v['bytes']/(1024*1024*1024):8.0f} GB"
        v['bytes_min'] = f"{v['bytes_min']:9.0f} b(min)"
        v['bytes_max'] = f"{v['bytes_max']/(1024*1024):9.1f} MB(max)"
        v['bytes']     = f"{v['bytes']:,} b"
        v['cnt_zerobyte']=f"{v['cnt_zerobyte']:3.0f} 0b"
        #Now order the dict for desired output
        keys_order=["cnt","bytesGB","bytes","bytes_max","bytes_min","cnt_zerobyte"]
        keys_remaining=list(v)  # use list to force copy of keys
        for key in keys_order:
            keys_remaining.remove(key)
            value=v.pop(key)
            # print(f"{key=} {v=}")
            if key in keys_order:
                v[key]=value
        for key in keys_remaining:
            v.pop(key)
    # Generate header from first[0] data_sorted entry[1] a dict
    headers=[ k for k,v in data_sorted[0][1].items()]
    headers.insert(0,"container")

    table_sorted=[[k, *v.values()] for k,v in data_sorted ]

    #
    print(tabulate(table_sorted, headers=headers, tablefmt=tablefmt, stralign="right")
                   , file=stream)


def process_string_to_dict(original_String):
    '''
    element='INFO: colorimages-resize/jpg-02232e14bd3789c2c7cb341c0d19688a_200_200; LastModifiedTime: 2021-01-20 01:45:08 +0000 GMT; VersionId: ; BlobType: BlockBlob; BlobAccessTier: Hot; ContentType: image/jpeg; ContentEncoding: ; LeaseState: available; LeaseDuration: ; LeaseStatus: unlocked;  Content Length: 522'
    '''
    try:
        result = dict((a.strip(), b.strip())
                         for a, b in (element.split(': ')
                                      for element in original_String.split('; ')))
        # Parse and simplify some data
        file = os.path.split(result['INFO'])
        result['path']=result['INFO']
        result['path_head']=file[0]
        result['path_tail']=file[1]
        result['bytes']=int(result['Content Length'])
    except BaseException as e:
        print(f"ERROR parsing {original_String=} {e=}")
        sys.exit(1)
    #
    return result

def inc_counts(counts,r):
    get_counts=counts.get(r['path_head'], {"cnt":0, "bytes": 0, "bytes_max": 0, "bytes_min": r['bytes'], "cnt_zerobyte": 0})
    counts[r['path_head']] = {"cnt": get_counts['cnt'] + 1
                             ,"bytes": get_counts['bytes'] + r['bytes']
                             ,"bytes_max": r['bytes'] if r['bytes'] > get_counts['bytes_max'] else get_counts['bytes_max']
                             ,"bytes_min": r['bytes'] if r['bytes'] < get_counts['bytes_min'] else get_counts['bytes_min']
                             ,"cnt_zerobyte": get_counts['cnt_zerobyte'] if r['bytes'] > 0 else get_counts['cnt_zerobyte'] + 1
                              }

def process_json1(f, args):
    if debug: print(f"process_json1 called.", file=sys.stderr)
    cnt=0
    counts=dict()
    for record in f:
        #d = json.loads(data)
        d = json.loads(record.decode("utf-8"))
        cnt+=1
        r = process_string_to_dict(d['MessageContent'])
        inc_counts(counts,r)
        if debug and cnt < 3:
            pprint(counts, tablefmt=args.tablefmt, stream=sys.stderr)
            print(f"{cnt:,=} {r=}", file=sys.stderr)
        if cnt % (10*1000*1000) == 0 or cnt == 1000000:
            t = time.perf_counter() - t_start
            print(file=sys.stderr)
            pprint(counts, tablefmt=args.tablefmt, stream=sys.stderr)
            print(f"progress {cnt=:,} time {t:>7.2f}s speed {round(cnt/t):,} /s  run time {round(t/60)}min", file=sys.stderr)
    t = time.perf_counter() - t_start
    #pprint(counts)
    pprint(counts, tablefmt=args.tablefmt, stream=sys.stderr)
    print(f"found {cnt=:,} records. time {t:.2f}s speed {round(cnt/t):,} /s ")



def process_json_gzip(process_function, args):
    print(f"#Start with file {args.inputfile}")
    #with zipfile.ZipFile(f_name, "r") as z:
    if ".gz" in args.inputfile.suffixes:
        try:
            with gzip.open(args.inputfile, "rb") as f:
                process_function(f, args)
        except gzip.BadGzipFile as error:
          print(f'ERROR gzip file error  {args.inputfile=} {error=}')
        except EOFError as e:
          print("End-Of-File when reading gzip input")
          sys.exit(1)
    else:
        with open(args.inputfile, "r") as f:
            process_function(f, args)

def parser():
    def validate_file(arg):
        if (file := pathlib.Path(arg).expanduser()).is_file():
            return file
        else:
            raise argparse.ArgumentTypeError(f"{arg} does not exist")
    parser = argparse.ArgumentParser(description='Generate blob usage report from azcopy list output file.')
    parser.add_argument('-i','--inputfile', type=validate_file,
                    help='Input file to read for json output from azcopy list',
                    default="~/az_list_tmprodsysstore-2023-01-07.json.gz")
    parser.add_argument('-o','--outputfile', type=str, default="report.txt",
                    help='Output report file. Not implemented yet, pipe to output.')
    parser.add_argument('-t','--tablefmt', type=str, default="jira",
                    help="set the tabular table format e.g. jira, html etc.")
    parser.add_argument('--verbose', '-v', action='count', default=0)
    return parser.parse_args()

if __name__ == "__main__":
    args=parser()
    global debug
    debug = args.verbose
    if debug: print(f"{args=}")
    process_json_gzip(process_json1, args=args)
    print("#The End.")
