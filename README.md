# Wikidata Lookup

This repo contains a Python package for verifying the authenticity for named entities in ReadAct.

The goal is to automately extract information about **person**, **space**, and **institutions** from **ReadAct**/data, then use Wikidata as an authenticity sources and compare information.

## The idea
#### Autenticity about Person
Two approaches are adopted: **lookup by name** or **query with Wikipedia links**.

For the former, names (include alt_name) are used to lookup with SPARQL query statements, and features like `family_name`, `first_name`, `alt_name`, `gender` or `sex`, `birthYear`, `deathYear`, `place_of_birth` are used in a  weighting mechanism to choose the most likely candidate.

For the latter, using MediaWiki API, Q-identifiers are acquired based on Wikipedia links and then be used for SPARQL queyring.

#### Autenticity about Space

Two APIs (OpenStreetMap and Wikidata) are under using.

#### Autenticity about Institution

Wikidata to be the authenticity source as well as the other named entities.



## Working Environment
Python3.8
MacOS/Linux

## Requirement on CSV
For pre-defined column names, check the definition in [Data Dictionary](https://github.com/readchina/ReadAct/blob/master/csv/data_dictionary.csv).

## How to use the current command line tool

#### Requirements

- Python3.8 or higher version.

- Required dependencies. Can be installed by:

  ```
  pip install -r requirements.txt		
  ```

#### Person Lookup

- Current version: 1.0.0

- Example:

  ```
  python3.8 -m src.scripts.command_line_tool src/CSV/Person.csv
  ```
  To read a user defined `Person.csv`, check the column names and to update it if necessary. Updated rows will be marked as modified by `SemBot` and the information of modifications will be added in `note`.
  
  The updating can be done based on:
  
  	-  `Wikidata id`
  	-  `family name` and  `first name`
  




