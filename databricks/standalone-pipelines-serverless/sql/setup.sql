-- Run once in the SQL editor. Change release_lab to your own catalog.

CREATE SCHEMA IF NOT EXISTS release_lab.mvst_demo;

-- Where the generator writes order files
CREATE VOLUME IF NOT EXISTS release_lab.mvst_demo.landing;
