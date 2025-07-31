from evaluator.eval import evaluator

if __name__ == "__main__":
    resume = open("sample/sample_resume.txt").read()
    job_des = open("sample/sample_job.txt").read()
    print(evaluator('Node, JS, .NET', 'Python, Node, JS'))
