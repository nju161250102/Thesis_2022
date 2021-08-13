import write_to_xls as wtx
# import get_line_version as glv
import filter as f
import compare_file as cf
import os
import get_commit_id as gci
import get_generic_bug_line as ggbl
import configure as c

no_anno_headers = ['commit id','file names','before','after']
res_file_path = c.res_path

# ******主流程函数******
def main_func():
    path = c.path
    # 获取commit id和数字对应的字典
    commit_id_file = res_file_path+'res/combine1.xls'
    no_anno_file_name = '1_no_anno_file'
    no_anno_file_path = res_file_path+'res/'+no_anno_file_name+'.xls'
    combine_1gobv_1naf_name = '1_final_res'
    combine_1gobv_1naf_path = res_file_path+'res/'+combine_1gobv_1naf_name+'.xls'
    generic_bug_line_file = '2_generic_bug_lines_with_now_version'
    generic_bug_line_path = res_file_path+"res/"+generic_bug_line_file+'.xls'
    add_del_lines_file = '2_add_del_lines_NoAnno_and_less4'
    add_del_lines_path = res_file_path+"res/"+add_del_lines_file+'.xls'
    only_bug_version_name = '1_get_only_bug_version'
    only_bug_version_path = res_file_path+'res/'+only_bug_version_name+'.xls'
    every_line_file_name = '2_5_from_show_every_lines'
    every_line_file_path = res_file_path+'res/'+every_line_file_name+'.xls'
    now_last_file_name = '2_now_last'
    now_last_file_path = res_file_path+'res/'+now_last_file_name+'.xls'

    # #####################################################################
    file_data = wtx.get_from_xls(commit_id_file)
    # cv = f.filter_not_bug_version(file_data)
    cv = wtx.get_from_xls(only_bug_version_path)

    # 过滤非java文件
    nmtn_changed_file,no_more_than_n = f.filter_more_than_n_version(file_data[0][0],cv,path,True,100)
    # print(len(no_more_than_n))
    print(len(nmtn_changed_file))

    # 过滤java文件中的注释，并更新修改文件数量
    if (os.path.exists(no_anno_file_path) == False):
        no_anno = f.filter_annotation(nmtn_changed_file,path)
        wtx.save_to_xls(no_anno_headers,no_anno,'test1',no_anno_file_name)
    # ################################################################################
    # 获取更新后符合要求的版本信息
    final_version_list = cf.combine_file1_file2(no_anno_file_path,0,8,only_bug_version_path,0,8,3,4)
    print('after filter , the final version list\'s length : '+str(len(final_version_list)))
    if (os.path.exists(combine_1gobv_1naf_path) == False):
        wtx.save_to_xls(final_version_list[0],final_version_list[1:],'res',combine_1gobv_1naf_name)
    else:
        print("file "+combine_1gobv_1naf_name+" is already exists")

    # 获取generic bug lines
    neigh_list = gci.get_neigh_commit_id_and_save(final_version_list[1:],commit_id_file,now_last_file_name)
    # ##################################################################
    res_no_anno = wtx.get_from_xls(combine_1gobv_1naf_path)
    commit_dict = gci.get_commit_id(commit_id_file,8,True)
    # 获取修改行
    if(os.path.exists(add_del_lines_path) == False):
        add_del_lines = ggbl.get_del_add_line(res_no_anno,add_del_lines_file,path,commit_dict)
    else:
        print("file "+add_del_lines_file+" is already exists")
    # ########################################################################
    # 获取generic-bug-fix-line
    add_del_lines_list = wtx.get_from_xls(add_del_lines_path)
    # print(add_del_lines_list)
    if(os.path.exists(generic_bug_line_path)==False):
        ggbl.get_generic_bug_lines(add_del_lines_list,path,generic_bug_line_file,commit_id_file)
    else:
        print("file "+generic_bug_line_file+" is already exists")
    generic_bug_lines = wtx.get_from_xls(generic_bug_line_path)

    # commit_dict_withoutNone = gci.get_commit_id(commit_id_file,8,False)
    commit_dict_withoutNone = gci.get_commit_id(commit_id_file,8)
    print(commit_dict_withoutNone)
    # #####################################################################
    # 获取遗漏的行
    commit_dict = gci.get_commit_id(commit_id_file,8,True)
    ggbl.split_show_to_every_lines(add_del_lines_file,every_line_file_name)
    cf.fix_lost_code_main(every_line_file_path,3,generic_bug_line_path,2,now_last_file_path,commit_dict,path)
    # ###################################################################
    # 验证结果
    # cf.verify_res_file(add_del_lines_path,0,only_bug_version_path,0)

if __name__ == "__main__":
    main_func()