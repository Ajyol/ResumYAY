from evaluator.evaluator import evaluator
from parser_scripts.job_parse import job_parser_from_file
from parser_scripts.resume_parser import parse_resume_file


if __name__ == "__main__":
    parsed_resume = parse_resume_file("sample/Resume.pdf")
    parsed_job_des = job_parser_from_file("sample/sample_job.txt")

    print(evaluator(parsed_resume, parsed_job_des))