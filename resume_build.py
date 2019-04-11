#!/usr/bin/env python3

import json
import os
from jinja2 import (Environment,
                    FileSystemLoader,
                    select_autoescape)


def find_projects(company_name, project_list):
    result = []
    for project in project_list:
        if project['company'] == company_name:
            result.append(project)
    return result


def sortable_date(project, date_key):
    date = project[date_key]
    date = date.split('/')
    date = '.'.join(date[::-1])
    return date


def correlate_projects(companies, projects):
    """relates projects to specific companies and order projects from
    newest-oldest"""
    result = list()
    for company in companies:
        project_list = find_projects(company['name'], projects)
        project_list.sort(key=lambda x: sortable_date(x, 'project_start'),
                          reverse=True)
        company['projects'] = project_list
    return companies
    
            


def load_json_files():
    with open('projects.json') as projects_fp:
        projects = json.load(projects_fp)
    with open('personal_info.json') as personal_info_fp:
        personal_info = json.load(personal_info_fp)
    with open('companies.json') as companies_fp:
        companies = json.load(companies_fp)
    companies = correlate_projects(companies=companies, projects=projects)
    return dict(personal_info=personal_info,
                companies=companies)


def main():
    json_data_load = load_json_files()
    env = Environment(loader=FileSystemLoader(os.getcwd()),
                      autoescape=select_autoescape(['html', 'xml']))
    resume_template = env.get_template('resume.j2')
    rendered_resume = resume_template.render(**json_data_load)
    print(rendered_resume)


if __name__ == "__main__":
    main()

