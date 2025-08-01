import json
from evaluator.eval import evaluator
from parser_scripts.job_des_parser import job_parser
from parser_scripts.resume_parser import parse_resume_file  # New import

if __name__ == "__main__":
    # Step 1: Parse resume PDF file into JSON
    parsed_resume = parse_resume_file("sample/Resume.pdf")

    # Save parsed resume to file
    # with open("sample/parsed_resume.json", "w", encoding="utf-8") as f:
    #     json.dump(parsed_resume, f, indent=2, ensure_ascii=False)

    # Step 2: Read and parse job description
    with open("sample/sample_job.txt") as f:
        job_des_text = f.read()
        job_des_json_str = job_parser(job_des_text)

    # Step 3: Evaluate
    #  result = evaluator(parsed_resume, job_des_json_str)

    # Step 4: Output
    # print(json.dumps(result, indent=2, ensure_ascii=False))

    print(parsed_resume)