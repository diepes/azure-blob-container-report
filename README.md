# Python script to summarize Azure blob storage usage

1. Generate json output of all blob files using Microsoft AzCopy tool.
   * Note this can be slow, e.g. 180M files, 69G, took 8h to list with 20mbps cap, zipped to 5GB.

   1. Download AzCopy from Microsoft - [https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10]

   2. Generate SAS token to access your blob storage, it needs [x] List
      * On huge blob storage this can take more thatn 24h make expiry a week.
      * export to env.

            export Azure_Sas_Url=""

   3. Run the azcopy list, this can take long if storage big (Terrabytes, Millions of files)

          time ./azcopy-macos list "${Azure_Sas_Url}" --machine-readable --output-type json --properties "LastModifiedTime;VersionId;BlobType;BlobAccessTier;ContentType;ContentEncoding" --cap-mbps 100 --running-tally  | gzip > ~/az_list_blob-$(date +%F).json.gz

   4. Check progress with

          ls -lh ~/az_list_blob-*

          time cat ~/az_list_blob-$(date +%F).json.gz|gunzip| wc -l | sed -e "s/[[:space:]][[:space:]]/ /g" | sed -e 's/^[[:space:]]//g' | numfmt --to=si

2. Generate report with this python prog

          python3 ./report_blob/report_blob.py -i ~/az_list_blob-$(date +%F).json.gz > report-$(date +%F).txt

## Example output (with -t html)

<table>
<thead>
<tr><th style="text-align: right;">               container</th><th style="text-align: right;">      cnt</th><th style="text-align: right;">  bytesGB</th><th style="text-align: right;">            bytes</th><th style="text-align: right;">    bytes_max</th><th style="text-align: right;">    bytes_min</th><th style="text-align: right;">  cnt_zerobyte</th></tr>
</thead>
<tbody>
<tr><td style="text-align: right;">      images1</td><td style="text-align: right;">       27</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">         62,009 b</td><td style="text-align: right;">  0.0 MB(max)</td><td style="text-align: right;">   519 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">            images2</td><td style="text-align: right;">        1</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">        169,490 b</td><td style="text-align: right;">  0.2 MB(max)</td><td style="text-align: right;">169490 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">            images3</td><td style="text-align: right;">       24</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">        818,432 b</td><td style="text-align: right;">  0.1 MB(max)</td><td style="text-align: right;">  1022 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">       images4</td><td style="text-align: right;">        4</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">      2,102,104 b</td><td style="text-align: right;">  1.0 MB(max)</td><td style="text-align: right;"> 33543 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">           report1</td><td style="text-align: right;">      161</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">      2,604,174 b</td><td style="text-align: right;">  0.2 MB(max)</td><td style="text-align: right;">  5164 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">    images5</td><td style="text-align: right;">      703</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">      3,241,566 b</td><td style="text-align: right;">  0.0 MB(max)</td><td style="text-align: right;">   281 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">           images6</td><td style="text-align: right;">      656</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">      8,531,504 b</td><td style="text-align: right;">  0.7 MB(max)</td><td style="text-align: right;">   823 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">           report2</td><td style="text-align: right;">      267</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     13,602,358 b</td><td style="text-align: right;">  0.1 MB(max)</td><td style="text-align: right;">  5126 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">        errors1</td><td style="text-align: right;">      173</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     14,050,777 b</td><td style="text-align: right;">  1.2 MB(max)</td><td style="text-align: right;">  5145 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">              users1</td><td style="text-align: right;">      220</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     18,230,688 b</td><td style="text-align: right;">  1.0 MB(max)</td><td style="text-align: right;">  9278 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">         error2</td><td style="text-align: right;">      305</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     27,510,955 b</td><td style="text-align: right;">  2.5 MB(max)</td><td style="text-align: right;">  5173 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">   images7</td><td style="text-align: right;">    3,198</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     33,570,690 b</td><td style="text-align: right;">  0.3 MB(max)</td><td style="text-align: right;">   305 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">       images8</td><td style="text-align: right;">    8,227</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     44,302,581 b</td><td style="text-align: right;">  0.1 MB(max)</td><td style="text-align: right;">   136 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">    errors3</td><td style="text-align: right;">   12,622</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">     74,007,047 b</td><td style="text-align: right;">  0.3 MB(max)</td><td style="text-align: right;">  5423 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">            errors4</td><td style="text-align: right;">   45,000</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">    166,897,802 b</td><td style="text-align: right;">  3.1 MB(max)</td><td style="text-align: right;">   406 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">images8</td><td style="text-align: right;">   16,783</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">    211,683,261 b</td><td style="text-align: right;">  0.6 MB(max)</td><td style="text-align: right;">   303 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">    images9</td><td style="text-align: right;">    4,629</td><td style="text-align: right;">     0 GB</td><td style="text-align: right;">    308,341,642 b</td><td style="text-align: right;">  1.4 MB(max)</td><td style="text-align: right;">    96 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">     images9</td><td style="text-align: right;">    9,649</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">    740,536,779 b</td><td style="text-align: right;">  4.8 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">          1 0b</td></tr>
<tr><td style="text-align: right;">              userimagesA</td><td style="text-align: right;">   15,000</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">    749,941,609 b</td><td style="text-align: right;">  2.7 MB(max)</td><td style="text-align: right;">    84 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">      userimagesB</td><td style="text-align: right;">   61,198</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">    857,806,656 b</td><td style="text-align: right;">  1.1 MB(max)</td><td style="text-align: right;">   305 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">   userimagesC</td><td style="text-align: right;">   55,000</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,047,880,398 b</td><td style="text-align: right;">  0.5 MB(max)</td><td style="text-align: right;">   279 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">     userimagesD</td><td style="text-align: right;">   54,697</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,083,548,739 b</td><td style="text-align: right;">  0.9 MB(max)</td><td style="text-align: right;">   269 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;"> userimagesE</td><td style="text-align: right;">   21,077</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,090,520,412 b</td><td style="text-align: right;">  1.6 MB(max)</td><td style="text-align: right;">   267 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">  export-reports</td><td style="text-align: right;">   15,676</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,136,073,132 b</td><td style="text-align: right;"> 17.1 MB(max)</td><td style="text-align: right;">  5183 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">  shippingreports</td><td style="text-align: right;">   21,290</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,208,945,757 b</td><td style="text-align: right;">  0.1 MB(max)</td><td style="text-align: right;">   122 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">    generalreports</td><td style="text-align: right;">   36,995</td><td style="text-align: right;">     1 GB</td><td style="text-align: right;">  1,512,532,337 b</td><td style="text-align: right;"> 19.6 MB(max)</td><td style="text-align: right;">  5351 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">   images10</td><td style="text-align: right;">   70,000</td><td style="text-align: right;">     2 GB</td><td style="text-align: right;">  2,301,267,403 b</td><td style="text-align: right;">  3.2 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">          1 0b</td></tr>
<tr><td style="text-align: right;">    images11</td><td style="text-align: right;">   55,000</td><td style="text-align: right;">     5 GB</td><td style="text-align: right;">  5,653,622,358 b</td><td style="text-align: right;"> 20.0 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">         38 0b</td></tr>
<tr><td style="text-align: right;">       images12</td><td style="text-align: right;">   70,000</td><td style="text-align: right;">     6 GB</td><td style="text-align: right;">  6,697,986,128 b</td><td style="text-align: right;">  1.7 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">          1 0b</td></tr>
<tr><td style="text-align: right;">     images13</td><td style="text-align: right;">   60,000</td><td style="text-align: right;">     7 GB</td><td style="text-align: right;">  7,643,115,428 b</td><td style="text-align: right;">  2.7 MB(max)</td><td style="text-align: right;">    99 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">     images14</td><td style="text-align: right;">   70,000</td><td style="text-align: right;">    10 GB</td><td style="text-align: right;"> 10,319,261,396 b</td><td style="text-align: right;">  1.5 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">          2 0b</td></tr>
<tr><td style="text-align: right;">    images15</td><td style="text-align: right;">   65,000</td><td style="text-align: right;">    17 GB</td><td style="text-align: right;"> 18,021,096,921 b</td><td style="text-align: right;">  1.6 MB(max)</td><td style="text-align: right;">    97 b(min)</td><td style="text-align: right;">          0 0b</td></tr>
<tr><td style="text-align: right;">     --- blob-totals ---</td><td style="text-align: right;">1,000,000</td><td style="text-align: right;">   498 GB</td><td style="text-align: right;">534,953,996,770 b</td><td style="text-align: right;">113.8 MB(max)</td><td style="text-align: right;">     0 b(min)</td><td style="text-align: right;">         43 0b</td></tr>
</tbody>
</table>

## The End
