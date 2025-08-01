import json
from evaluator.eval import evaluator
from parser_scripts.job_des_parser import job_parser

if __name__ == "__main__":
    with open("sample/sample_resume.json") as f:
        resume = json.load(f)

    with open("sample/sample_job.txt") as f:
        job = f.read()
        job_des_json_str = job_parser(job)
        job_des = json.loads(job_des_json_str)

    print(evaluator(resume, job_des))
