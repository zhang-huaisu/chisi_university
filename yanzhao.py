# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 13:17:48 2018

@author: admin
"""

# -*- coding: utf-8 -*-
# @Author : Keginx
# Date : 2018/9/13
import requests
from bs4 import BeautifulSoup
import ast
import pandas as pd


class University:
    def __init__(self):
        self.head = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept - Language': 'zh - CN, zh;q = 0.9',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKi"
                          "t/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
        }
        self.data = []
        # 学科
        self.major = []
        # 学科对应的最大页数
        self.max_page = []

    def get_list_fun(self, url, name):
        """获取提交表单代码"""
        response = requests.get(url, headers=self.head)
        province = response.json()
        with open("{}.txt".format(name), "w") as f:
            for x in province:
                f.write(str(x))
                f.write("\n")
            f.close()

    # 写入文件
    def write_to_txt(self, name, data):
        with open("file/{}.txt".format(name), "w") as f:
            for x in data:
                f.write(str(x))
                f.write("\n")
            f.close()

    def write_to_csv(self, name, data_list):
        data=pd.DataFrame(data_list)
        df=pd.DataFrame(data,columns=['招生单位','所在地','院校特性','研究生院','自划线院校','博士点'])    
        
        #dataframe = pd.DataFrame(data_list[0], index=[0])
        # 将DataFrame存储为csv,index表示是否显示行名，default=True
        # dataframe.to_csv("file/{}.csv".format(name), index=False, sep=',', mode='w')
        #for i in range(1, len(data_list)):
            #dataframe.append(data_list[i], ignore_index=True)
        df.to_csv("file/{}.csv".format(name), index=False, sep=',', mode='w',encoding="utf_8_sig")

    def get_list(self):
        """
        分别获取省，学科门类，专业编号数据
        写入txt文件
        """
        self.get_list_fun("http://yz.chsi.com.cn/zsml/pages/getSs.jsp", "province")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getMl.jsp', "category")
        self.get_list_fun('http://yz.chsi.com.cn/zsml/pages/getZy.jsp', 'major')

    
    #获取所有学科类别


    def get_major(self):
        response = requests.get('http://yz.chsi.com.cn/zsml/pages/getZy.jsp', headers=self.head)
        self.major = response.json()


    #获取每门学科对应的最大页数
    

    def get_max_page_by_major(self):
        self.get_major()
        url = 'https://yz.chsi.com.cn/zsml/queryAction.do'
        # 学习方式 全日制:1,非全日制:2
        for method in range(1, 3):
            # 保存学科信息和该学科对应最大页数
            dict_list = []
            # 学科
            for major in self.major:
                form_data = {'yjxkdm': major['dm'], 'xxfs': method}
                response = requests.post(url, headers=self.head, data=form_data)
                response.encoding=response.apparent_encoding
                html = response.text
                soup = BeautifulSoup(html, features='lxml')
                # 获取网页中该学科对应页码
                # 例如[<li class="lip unable lip-first"><i class="iconfont"></i></li>, <li class="lip selected"><a href="#" onclick="nextPage(1)">1</a></li>, <li class="lip "><a href="#" onclick="nextPage(2)">2</a></li>, <li class="lip "><a href="#" onclick="nextPage(3)">3</a></li>, <li class="lip "><a href="#" onclick="nextPage(4)">4</a></li>, <li class="lip "><a href="#" onclick="nextPage(5)">5</a></li>, <li class="lip dot">...</li>, <li class="lip"><a href="#" onclick="nextPage(12)">12</a></li>, <li class="lip "><a href="#" onclick="nextPage(2)"><i class="iconfont"></i></a></li>, <li class="lip lip-input-box clearfix lip-last"><input class="page-input" id="goPageNo" name="goPageNo" type="text" value=""/><input class="page-btn" onclick="goPageNo()" type="button" value="Go"/></li>]
                pageno_content_list = soup.find_all('li', {'class': ['lip selected', 'lip', 'lip ']})
                pageno_list = []
                for content in pageno_content_list:
                    if content.get_text().isdigit():
                        pageno_list.append(content.get_text())
                # 最大页数
                max_no = max(pageno_list)
                # 字典保存学科类别和代码以及最大页数
                dict = major
                dict['max_no'] = max_no
                dict_list.append(dict)
                print("获取信息:", dict)
            # 保存信息
            self.write_to_txt(method, dict_list)

        print("已获取所有学科对应最大页数,请查看文件1.txt(全日制)和2.txt(非全日制)") 

    def get_university_info(self):
        
        url = 'https://yz.chsi.com.cn/zsml/queryAction.do'
        # 学习方式 全日制:1,非全日制:2
        for method in range(1, 3):
            info_list = []
            with open(u'file/' + str(method) + '.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    info_list.append(ast.literal_eval(line))
            # 遍历学科
            for major in info_list:
                # 保存单科所有招生院校信息
                #subject_list=[]
                data_list = []
                # 遍历页码
                for no in range(1, int(major['max_no']) + 1):
                    form_data = {'yjxkdm': major['dm'], 'xxfs': method, 'pageno': no}
                    response = requests.post(url, headers=self.head, data=form_data)
                    response.encoding=response.apparent_encoding
                    #r.encoding = r.apparent_encoding
                    html = response.text
                    soup = BeautifulSoup(html, features='lxml')
                    # 每页对应的校名列表标签内容
                    # 表格中每一行对应html 组成的列表
                    # 例如[<td>
                    # <form action="/zsml/queryAction.do" id="form3" method="post" name="form3">
                    # <a href="/zsml/querySchAction.do?ssdm=11&amp;dwmc=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6&amp;mldm=&amp;mlmc=&amp;yjxkdm=0101&amp;xxfs=1&amp;zymc=" target="_blank">(10001)北京大学</a>
                    # </form>
                    # </td>, <td>(11)北京市</td>, <td class="ch-table-center"><span class="ch-table-tag">985</span> <span class="ch-table-tag">211</span></td>, <td class="ch-table-center"><i class="iconfont ch-table-tick"></i></td>, <td class="ch-table-center"><i class="iconfont ch-table-tick"></i></td>, <td class="ch-table-center"><i class="iconfont ch-table-tick"></i></td>, <td>
                    # <form action="/zsml/queryAction.do" id="form3" method="post" name="form3">
                    # <a href="/zsml/querySchAction.do?ssdm=11&amp;dwmc=%E4%B8%AD%E5%9B%BD%E4%BA%BA%E6%B0%91%E5%A4%A7%E5%AD%A6&amp;mldm=&amp;mlmc=&amp;yjxkdm=0101&amp;xxfs=1&amp;zymc=" target="_blank">(10002)中国人民大学</a>
                    # </form>]
                    line_list_html = soup.select('tbody tr')
                    try:                        
                        for line_html in line_list_html:
                            #print(line_html)
                            data = {'招生单位': '', '所在地': '', '院校特性': '', '研究生院': '', '自划线院校': '', '博士点': ''}
                            # 重新构造html 在开头加上<html>末尾加上</html>,方便调用BeautifulSoup方法获取标签中的内容
                            tempsoap = BeautifulSoup("<html>" + str(line_html) + "</html>", features='lxml')
                            # 校名 招生单位
                            university = tempsoap.find('a').get_text()
                            # 省市 (select()返回的的type是list,td:nth-of-type(2)表示获取第二个td)
                            province = tempsoap.select('td:nth-of-type(2)')[0].get_text()
    
                            # 院校特性
                            peculiarity = tempsoap.select('td:nth-of-type(3)')[0].get_text()
                            # 特性不为空
                            if not (peculiarity == u' '):
                                #     #985
                                is985 = tempsoap.select('td span:nth-of-type(1)')[0].get_text()
                                #     # #211
                                #     str = ' '
                                is211 = tempsoap.select('td span:nth-of-type(2)')[0].get_text()
                                # 非985
                                if is985 == u'':
                                    # 去掉211前的空格
                                    peculiarity = is211
                                else:
                                    peculiarity = is985 + u' ' + is211
    
                            # 研究生院
                            is_graduate_schools = tempsoap.select('td:nth-of-type(4)')[0].get_text()
                            if not (is_graduate_schools == u' '):
                                is_graduate_schools = '是'
                            else:
                                is_graduate_schools = '否'
    
                            # 自划线
                            independent_recruitment_line = tempsoap.select('td:nth-of-type(5)')[0].get_text()
                            if not (independent_recruitment_line == u' '):
                                independent_recruitment_line = '是'
                            else:
                                independent_recruitment_line = '否'
    
                            # 博士点
                            doctor_station = tempsoap.select('td:nth-of-type(6)')[0].get_text()
                            if not (doctor_station == u' '):
                                doctor_station = '是'
                            else:
                                doctor_station = '否'
                            # data = {'招生单位': '', '所在地': '', '院校特性': '', '研究生院': '', '自划线院校': '', '博士点': ''}
                            data['招生单位'] = university
                            data['所在地'] = province
                            data['院校特性'] = peculiarity
                            data['研究生院'] = is_graduate_schools
                            data['自划线院校'] = independent_recruitment_line
                            data['博士点'] = doctor_station                        
                           
                            data_list.append(data)
                    except:
                            print('获取'+major['dm'] + '_' + major['mc'] + '_' + '全日制'+'!!!'+'失败')
                        #print(major, data)

                        # print(university, province, 'x' + peculiarity + 'x', is_graduate_schools,independent_recruitment_line,doctor_station, peculiarity == u' ',
                        #       is_graduate_schools == u' ')
                if method == 1:
                    file_name = major['dm'] + '_' + major['mc'] + '_' + '全日制'
                    self.write_to_csv(file_name, data_list)
                else:
                    file_name = major['dm'] + '_' + major['mc'] + '_' + '非全日制'
                    self.write_to_csv(file_name, data_list)

                print('\n学科: ' + major['dm'] + '_' + major['mc'] + ' 数据获取完成\n')


if __name__ == '__main__':
    university = University()
    # university.get_list()
    university.get_max_page_by_major()
    university.get_university_info()
    # list = [{'招生单位': '1 ', '所在地': ' 1', '院校特性': '1', '研究生院': '1', '自划线院校': '1', '博士点': '1'},
    #         {'招生单位': '2', '所在地': '2', '院校特性': '', '研究生院': '2', '自划线院校': '2', '博士点': '2'}]
    # university.write_to_csv("test", list)
