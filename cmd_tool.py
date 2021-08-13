import os

def change_path_to_target(path):
    commendline = path
    res= os.chdir(commendline)
    # print(res)

def run_command(command):
    com_res = os.popen(command)
    com_res = com_res.buffer.read().decode(encoding = 'utf-8',errors = 'ignore')
    return com_res.split('\n')

if __name__ == "__main__":
    # change_path_to_target('E:\\projects\\git\\mooctest\\tika-1\\')
    # run_command('git log')
    x = '-        private float duration;'
    print('d4a39b4873 tika-parser-modules/tika-parser-integration-tests/src/test/java/org/apache/tika/parser/pdf/PDFParserTest.java                  1) /*'.split(')',maxsplit=1)[1].strip())