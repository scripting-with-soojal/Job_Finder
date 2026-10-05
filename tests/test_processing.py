import unittest

from job_finder.models import Job
from job_finder.processing import (
    deduplicate_jobs,
    extract_experience,
    extract_keywords,
    strip_html,
)


def make_job(**kw):
    base = dict(source="X", company="Acme", title="Data Engineer",
                location="Mumbai", description="", apply_url="")
    base.update(kw)
    return Job(**base)


class TestExperience(unittest.TestCase):
    def test_range(self):
        self.assertEqual(extract_experience("We need 3-5 years of Python"), "3-5 Years")
        self.assertEqual(extract_experience("3 to 5 years experience"), "3-5 Years")

    def test_minimum_and_plus(self):
        self.assertEqual(extract_experience("minimum 4 years"), "4+ Years")
        self.assertEqual(extract_experience("5+ years of experience"), "5+ Years")

    def test_not_specified(self):
        self.assertEqual(extract_experience("Great team"), "Not Specified")
        self.assertEqual(extract_experience(""), "Not Specified")


class TestKeywords(unittest.TestCase):
    def test_finds_skills(self):
        found = extract_keywords("PySpark, Airflow and BigQuery on AWS with dbt. Power BI a plus")
        self.assertEqual(set(found), {"PySpark", "Airflow", "BigQuery", "AWS", "dbt", "Power BI"})

    def test_word_boundaries(self):
        # "Spark" must not match inside "PySpark"; "dbt" not inside other words
        self.assertNotIn("Spark", extract_keywords("We use PySpark"))
        self.assertNotIn("dbt", extract_keywords("undbtable"))


class TestDedupe(unittest.TestCase):
    def test_by_url_case_insensitive(self):
        jobs = [make_job(apply_url="HTTPS://a.com/1"), make_job(apply_url="https://a.com/1")]
        self.assertEqual(len(deduplicate_jobs(jobs)), 1)

    def test_fallback_key_when_no_url(self):
        jobs = [make_job(), make_job(), make_job(location="Pune")]
        self.assertEqual(len(deduplicate_jobs(jobs)), 2)


class TestStripHtml(unittest.TestCase):
    def test_escaped_html(self):
        self.assertEqual(strip_html("&lt;p&gt;Hello &lt;b&gt;World&lt;/b&gt;&lt;/p&gt;"), "Hello World")


if __name__ == "__main__":
    unittest.main()
