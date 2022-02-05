#!/bin/python3

# Read Cherry Tree file and convert to LaTeX
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Author: Francisco Perez <paco.perez@gmail.com>

import os
import argparse
import codecs
import base64
from typing import Counter

import xml.etree.ElementTree as ET

# label default Report OSCP for LaTeX
PATH_IMAGES = "_latex"
TAGS_REPORT = 'report'
TAGS_IMAGE = 'image'
TAGS_TEXT = 'rich_text'
# replace characters not allowed in LaTeX
REPLACE_CHAR_ESP = [['❯','$']] #


class CT2LaTeX:

    def __init__(self, file, output, debug):
        self.cherrytree = None
        self.file = file
        self.output = output
        self.debug = debug
        if self.file is not None:
            self.path_out = self.file+PATH_IMAGES
        self.node_report = None
        self.main()

    def main(self):
        # read file
        if self.file is not None:
            if self.debug:
                print("Reading file: " + self.file)
            if self.output is not None:
                if self.debug:
                    print("Writing file: " + self.output)
                    fname = self.output
                f = codecs.open(self.output, 'w', "utf-8")
            else:    
                fname = self.file.split('.')
                fname = fname[0] + '.tex' 
                f = codecs.open(fname , 'w', "utf-8")
             
            with open(self.file, 'r') as fint:

                # convert ctd to ET nodes
                self.cherrytree = ET.parse(fint)
                # search node_report to start convert
                self.search_tags2node(self.cherrytree.getroot(),TAGS_REPORT)
                # create dir images_latex
                if not os.path.exists(self.path_out):
                    os.makedirs(self.path_out)
                # convert report to LaTeX
                self.report2latex(f)
                  
            fint.close()    
            f.close()

            # replace char especial from file to latex
            self.replace_char_especial(fname)

    def replace_char_especial(self,file):
       
        for chars in REPLACE_CHAR_ESP:
            fint = codecs.open(file, 'r', "utf-8")
            content = fint.read()
            content = content.replace( chars[0], chars[1])
            fint.close()
            fout = codecs.open(file, 'w', "utf-8")
            fout.write(content)
            fout.close()
        
        
            
    def search_tags2node(self,tree,tags):
        
        node_root = tree
        
        for level in list(node_root):
            if level.tag == 'node' and level.text is not None:
                if self.debug:
                    print("level.node.name: "+str(level.attrib['name']))
                if level.attrib['tags'] == tags:
                    self.node_report = level
                    break
                else:
                    self.search_tags2node(level,tags)
  
        

    def report2latex(self, f):

        if self.node_report.tag == 'node' and self.node_report.text is not None:

            f.write('\\documentclass[a4paper]{report} % format template report OSCP to use\n\n\\usepackage[utf8]{inputenc}\n\\usepackage{graphicx}\n')
            f.write('\\usepackage{fancyhdr}\n')
            f.write('\\usepackage[left=2.5cm,top=2.5cm,right=2.5cm,bottom=5cm]{geometry}\n')
            f.write('\\usepackage{anyfontsize}\n')
            f.write('\\usepackage{longtable}\n')
            f.write('\\usepackage{adjustbox}\n')
            # show code in latex
            f.write('\\usepackage{listings}\n')
            f.write('\\renewcommand{\\headrulewidth}{0pt}\n')
            # reset format page style
            f.write('\\fancyhf{}\n')
            # generate table with multiple rows
            f.write('\\usepackage{multirow}\n')
            # add color to table
            f.write('\\usepackage[table,xcdraw]{xcolor}\n')
            f.write('% If you use beamer only pass "xcolor=table" option, i.e. \documentclass[xcolor=table]{beamer}\n')
            f.write('\n\n')
            # path images
            f.write("\\graphicspath{ {./%s/} }"%self.path_out)
            f.write('\n')
            # show subsubsection in "Table of Contents"
            f.write('\\setcounter{tocdepth}{3}\n')
            f.write('\\setcounter{secnumdepth}{3}\n')
            # search node front_page
            self.search_tags2node(self.node_report,'front_page')
            # add header front_page
            f.write('\\fancyhead[C]{\\includegraphics[width=\\textwidth]{'+self.convert2latex(self.node_report ,'head_image')+'}}\n')
            
            f.write('\n\n')
            f.write('\\begin{document}\n\n')

            # add front page
            self.add_front_page(self.node_report, f)
            
            f.write('\\tableofcontents\n')
            f.write('\\fancyfoot[R]{\\thepage\,-\,Page}\n')
            f.write('\\thispagestyle{fancy}\n')
            
            # add body
            self.search_tags2node(self.cherrytree.getroot(),'chapter1')
            self.add_chatper_body(self.node_report, f)
            self.search_tags2node(self.cherrytree.getroot(),'chapter2')
            self.add_chatper_body(self.node_report, f)
            self.search_tags2node(self.cherrytree.getroot(),'chapter3')
            self.add_chatper_body(self.node_report, f)
            self.search_tags2node(self.cherrytree.getroot(),'chapter4')
            self.add_chatper_body(self.node_report, f)
            # add new body chapter here

            # add page footer
            f.write('\\end{document}\n')
                

    def add_front_page(self, node_front_page, f):

        f.write('\\begin{titlepage}\n')   
        f.write('   \\chapter*{\\centering\\vspace{0.4cm}\\fontsize{33}{10}\\selectfont  '+self.convert2latex(node_front_page ,'Title')+'}\n')
        f.write('   \\centering\n')
        f.write('   {\\vspace{-0.5cm}\\fontsize{25}{10}\\selectfont\\textbf{'+self.convert2latex(node_front_page ,'Subtitle1')+'}\\par}\n')
        f.write('   {\\vspace{0.5cm}\\fontsize{25}{10}\\selectfont\\textbf{'+self.convert2latex(node_front_page ,'Subtitle2')+'}}\n')
        f.write('   \\includegraphics[width=\\textwidth,height=0.05cm]{'+self.convert2latex(node_front_page ,'line_image')+'}\\par\\vspace{1cm}\n')
        f.write('   {\\vspace{-0.5cm}\\Large{'+self.convert2latex(node_front_page ,'Version')+'}\\par}\n')
        f.write('   {\\vspace{0.7cm}\\Large{'+self.convert2latex(node_front_page ,'E-mail')+'}\\par}\n')
        f.write('   {\\vspace{0.7cm}\\huge\\bfseries{'+self.convert2latex(node_front_page ,'OSID')+'}\\par}\n')
        f.write('   \\vspace{1cm}\n')
        f.write('   \\vfill\n')
        f.write('   \\includegraphics[width=0.5\\textwidth]{'+self.convert2latex(node_front_page ,'foot_image')+'}\\par\\vspace{1cm}\n')
        f.write('% Bottom of the page\n')
        f.write('   {\\vspace{0.25cm}\\normalsize{'+self.convert2latex(node_front_page ,'Copyright1')+'}\\par}\n')
        f.write('   {\\vspace{0.25cm}\\small{'+self.convert2latex(node_front_page ,'Copyright2')+'}\\par}\n')
        f.write('   \\thispagestyle{fancy}\n')
        f.write('\\end{titlepage}\n')

    def convert2latex(self, node, name):
        value_result = ''
        
        
        for node_level in list(node):
            if node_level.tag == 'node' and node_level.attrib is not None :
                if  node_level.attrib['tags'] == 'text' and node_level.attrib['name'] == name :
                    for value in list(node_level):
                        if self.debug:
                            print("value.tag: "+str(value.tag))
                        if value.tag == TAGS_TEXT and value.text is not None:
                            if self.debug:
                                print("convert_text2latex: "+str(name))
                            value_result = str(value.text)
                        
            if node_level.tag == 'node' and node_level.attrib is not None :
                if node_level.attrib['tags'] == TAGS_IMAGE and node_level.attrib['name'] == name :
                    for value_image in list(node_level):
                        if self.debug:
                            print("value_image.tag: "+str(value_image.tag))
                        if value_image.tag == 'encoded_png' and value_image.text is not None:
                            if self.debug:
                                print("convert_image2latex: "+str(name))
                            code = base64.b64decode(value_image.text)
                            value_text = 'image_%s.png'%name
                            file_png = open(self.path_out+"/"+value_text, "wb")
                            file_png.write(code)
                            file_png.close()
                            value_result = str(value_text)
                       
        return(value_result)

    def add_chatper_body(self, node_body, f):
            
            if node_body.tag == 'node' and node_body.text is not None:
                f.write('\\chapter{'+str(node_body.attrib['name'])+'}\n')
                for level in list(node_body):
                    if level.tag == 'node' and level.attrib['tags'] is not None:
                        if level.attrib['tags'] == 'section':
                            f.write('\\section{'+str(level.attrib['name'])+'}\n')
                            self.add_body_node( level, f)
                            f.write('\\thispagestyle{fancy}\n') 
                            for level2 in list(level):
                                if level2.tag == 'node' and level2.attrib['tags'] is not None:
                                    if level2.attrib['tags'] == 'subsection':
                                        self.add_subsection_body(level2, f)
                                else:
                                    self.add_body_node(level2, f) 
                        else:
                            self.add_body_node(level, f)
                    else:
                        self.add_body_node(node_body, f)   


    def add_subsection_body(self, node_body, f):
            
            if node_body.tag == 'node' and node_body.text is not None:
                f.write('\\subsection{'+str(node_body.attrib['name'])+'}\n')
                for level3 in list(node_body):
                    if level3.tag == 'node' and level3.attrib['tags'] is not None:
                        if level3.attrib['tags'] == 'subsubsection':
                            f.write('\\subsubsection{'+str(level3.attrib['name'])+'}\n')
                            self.add_body_node( level3, f)
                            f.write('\\thispagestyle{fancy}\n') 
                        else:
                            self.add_body_node(node_body, f)
                    else:
                        self.add_body_node(level3, f)
            else:
                self.add_body_node(node_body, f)

    def add_body_node(self, node_body, f):
        if node_body.tag == 'node' and node_body.text is not None:
            count=0
            for value in list(node_body):
                if value.tag == 'node' and value.text is not None:
                    if self.debug:
                        print("add_body_node: "+str(value.text))
                    if value.attrib['tags'] == 'text':
                        count+=1
                        f.write(self.convert2latex(node_body,'Text'+str(count))+'\n')
                    if value.attrib['tags'] == TAGS_IMAGE:
                        f.write('\\begin{center}\n')
                        f.write('\\includegraphics{'+self.convert2latex(node_body,str(value.attrib['name']))+'}\\par\n')
                        f.write('\\end{center}\n')
                    


def main():
    print("Convert Cherry Tree file to LaTeX")
    print("Copyright (C) 2022 Francisco Perez") 
    print("This program comes with ABSOLUTELY NO WARRANTY.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions; see the GNU General Public License for")
    print("more details.")
    print("")

    # read arguments
    parser = argparse.ArgumentParser(description='Convert Cherry Tree file to LaTeX')
    parser.add_argument('-f', '--file', help='Cherry Tree file to convert')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    args = parser.parse_args()    

    CT2LaTeX(args.file, args.output, args.debug)



# python3 cherry2latex.py -f Inform_OSCP_Template.ctd -o salida.tex -d
# latexmk -pdf -pvc  Inform_OSCP_Template.tex
# https://en.wikibooks.org/wiki/LaTeX/Title_Creation

'''
Estructura de arbol con nodos 
image_nombre_unico
text1
image_nombre_unico
text2
text3 

(tipos nodo que se recorren en orden y el contenido es solo una imagen o texto) que es lo que se añade luego en el informe
en cada nodo padre al que corresponde.

'''

if __name__ == "__main__":
    main()




