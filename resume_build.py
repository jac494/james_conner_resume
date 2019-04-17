#!/usr/bin/env python3

"""Converts json files representing resume data into html and pdf files"""

import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit


TEMPLATES = [
    'templates/projects_resume.j2',
    'templates/experience_resume.j2'
    ]

PDFKIT_OPTIONS = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in'
    }
    
DATAFILES = {
    'projects': 'data/projects.json',
    'personal_info': 'data/personal_info.json',
    'companies': 'data/companies.json',
    }
    
OUTPUT = 'output_files'

def find_projects(company_name, project_list):
    """returns list of projects associated with company_name
    :param company_name: name of company to return projects for
    :type company_name: str
    :param project_list: list of projects as dictionaries
    :type project_list: list

    :return: list
    """
    result = []
    for project in project_list:
        if project['company'] == company_name:
            result.append(project)
    return result


def sortable_date(project, date_key):
    """converts dates in format mm/yyyy to yyyy.mm for generic string sorting
    :param project: project dictionary
    :type project: dict
    :param date_key: key for locating the date in the project
    :type date_key: str
    
    :return: str
    """
    date = project[date_key]
    date = date.split('/')
    date = '.'.join(date[::-1])
    return date


def technologies_set(projects, sorted=True):
    """return a list of unique technologies for all given projects
    :param projects: list of projects as dictionaries
    :type projects: list
    :param sorted: whether or not to return a sorted list
    :type sorted: bool

    :return: list
    """
    tech_set = set()
    for project in projects:
        tech_set.update(project['technologies'])
    tech_set = list(tech_set)
    if sorted:
        tech_set.sort()
    return tech_set


def correlate_projects(companies, projects):
    """relates projects to specific companies and order projects from newest
    to oldest
    :param companies: list of companies as dictionaries
    :type companies: list
    :param projects: list of projects as dictionaries
    :type projects: list

    :return: list
    """
    for company in companies:
        project_list = find_projects(company['name'], projects)
        project_list.sort(key=lambda x: sortable_date(x, 'project_start'),
                          reverse=True)
        company['projects'] = project_list
        company['all_technologies'] = technologies_set(project_list)
    return companies


def load_json_files():
    """loads necessary json files into dictionaries"""
    with open(DATAFILES['projects']) as projects_fp:
        projects = json.load(projects_fp)
    with open(DATAFILES['personal_info']) as personal_info_fp:
        personal_info = json.load(personal_info_fp)
    with open(DATAFILES['companies']) as companies_fp:
        companies = json.load(companies_fp)
    companies = correlate_projects(companies=companies, projects=projects)
    return dict(personal_info=personal_info,
                companies=companies)

def base_filename(template_path):
    """strips path members and file extensions to return a file's name
    :param template_path: path of specified template file
    :type template_path: str

    :return: str
    """
    fname = template_path.split(os.sep)[-1]
    base_name = '.'.join(fname.split('.')[:-1])
    return base_name


def create_resume_files(jinja_env, template_path, template_data):
    """correlates resume data into html and pdf files and writes them
    to global OUTPUT directory"""
    resume_template = jinja_env.get_template(template_path)
    rendered_resume = resume_template.render(**template_data)
    base_name = base_filename(template_path)
    html_file = os.sep.join([OUTPUT, base_name + '.html'])
    pdf_file = html_file[:-4] + 'pdf'
    with open(html_file, 'w') as outfile:
        outfile.write(rendered_resume)
    pdfkit.from_file(html_file, pdf_file, options=PDFKIT_OPTIONS)
    

def make_data_dir():
    """creates output directory specified in global OUTPUT"""
    try:
        os.mkdir(OUTPUT)
    except FileExistsError:
        pass


def main():
    """verifies output path structure and creates html and pdf resumes
    based on json data files"""
    make_data_dir()
    json_data_load = load_json_files()
    env = Environment(loader=FileSystemLoader(os.getcwd()),
                      autoescape=select_autoescape(['html']))
    for template_path in TEMPLATES:
        create_resume_files(jinja_env=env,
                            template_path=template_path, 
                            template_data=json_data_load)


if __name__ == "__main__":
    main()

