-- DATABASESCHEMA 

DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS data;


CREATE TABLE country (
    district_name VARCHAR(255), 
    district_geom MULTIPOLYGON()
	country_code VARCHAR(3),
	country_name VARCHAR(255),
    PRIMARY KEY (country_code)
);

CREATE TABLE data (
    country_code VARCHAR(3),
    year INT,
    co2_emission FLOAT,
    gdp FLOAT ,
    population_relative FLOAT,
    population_total FLOAT,
    electricity_production_renewable FLOAT,
    PRIMARY KEY (country_code, year)
);