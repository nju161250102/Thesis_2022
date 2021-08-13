import xlwt
import xlrd
import configure as c

# 将list保存到xls文件中
def save_to_xls(headers,res,pro_name,res_file):
    row = 0
    line = 0
    xls = xlwt.Workbook()
    sht1 = xls.add_sheet(pro_name)
    for i in headers:
        sht1.write(row,line,i)
        line = line + 1
    row = row + 1
    line = 0
    for i in res:
        # print(row)
        for j in i:
            # print(j)
            sht1.write(row,line,j)
            line = line + 1
        line = 0
        row = row + 1
    xls.save(c.res_path+'res/'+res_file+".xls")

def save_to_init_xls(headers,res,pro_name,res_file):
    row = 0
    line = 0
    xls = xlwt.Workbook()
    sht1 = xls.add_sheet(pro_name)
    for i in headers:
        sht1.write(row,line,i)
        line = line + 1
    row = row + 1
    line = 0
    for i in res:
        # print(row)
        for j in i:
            # print(j)
            sht1.write(row,line,j)
            line = line + 1
        line = 0
        row = row + 1
    xls.save(c.res_path+'init_data/'+res_file+".xls")

def get_from_xls(path,start_line= 1):
    wb = xlrd.open_workbook(path)
    ws = wb.sheets()[0]
    rows = list(ws.get_rows())
    ret = []
    for row in rows[start_line:]:
        this_res = []
        for j in row:
            this_res.append(j.value)
        ret.append(this_res)
    return ret

if __name__ == "__main__":
    # ret = get_from_xls('res/only_java_changed_numlessthan4_and_bugfixversion.xls')
    # print(ret)
    # print(len('//asdads'.split('//')))

    str = 'tika-parsers/src/main/java/org/apache/tika/parser/mp3/MpegStream.java**-            skipStream(in, currentHeader.getLength() - HEADER_SIZE);**-    /****-    private static void skipStream(InputStream in, long count)**-            throws IOException**-    {**-        long size = count;**-        long skipped = 0;**-        while (size > 0 && skipped >= 0)**-        {**-            skipped = in.skip(size);**-            if (skipped != -1)**-            {**-                size -= skipped;**-            }**-        }**-    }**-    '
    ad = str.split('**')[1:]
    print(ad)
    for i in ad:
        print(i+"********"+i[1:].strip())