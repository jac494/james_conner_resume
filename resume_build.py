#!/usr/bin/env python3

import json
import os
from jinja2 import (Environment,
                    FileSystemLoader,
                    select_autoescape)


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


def technologies_set(projects):
    tech_set = set()
    for project in projects:
        tech_set.update(project['technologies'])
    tech_set = list(tech_set)
    tech_set.sort()
    return tech_set


def correlate_projects(companies, projects):
    """relates projects to specific companies and order projects from
    newest-oldest"""
    for company in companies:
        project_list = find_projects(company['name'], projects)
        project_list.sort(key=lambda x: sortable_date(x, 'project_start'),
                          reverse=True)
        company['projects'] = project_list
        company['all_technologies'] = technologies_set(project_list)
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
    for template_path in TEMPLATES:
        resume_template = env.get_template(template_path)
        rendered_resume = resume_template.render(**json_data_load)
        out_html_file = '.'.join(template_path.split('.')[:-1])
        out_html_file += '.html'
        print(rendered_resume)
        with open(out_html_file, 'w') as outfile:
            outfile.write(rendered_resume)


if __name__ == "__main__":
    main()

