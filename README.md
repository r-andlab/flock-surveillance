# flock-surveillance
This repository contains code to systematically discover Flock transparency portals via search engines, as well as scrape code from transparency portals.

## scripts
**create-search-terms**: generates search terms for search engines from city and county names, e.g. santa-cruz-ca.

**full-url-discovery**: Scrapes Brave or Google for generated search terms and employs proxy rotation to avoid bot detection.

**sample-url-discovery**: Scrapes DuckDuckGo for any URLs matching "site:transparency.flocksafety.com." This was used to profile transparency portals and Flock URLs for further study.

**scrape-urls**: employs proxy rotation to scrape dynamic javescript of Flock transparency portals.

## data
Contains output data from transparency portal searching that is used when we scrape all found transparency portals. Also contains city and county information used to generate search terms and screenshots of the Wichita, Kansas portal as a motivating example for this project.

## analysis
**analyze-scrapes**: Analyzes the data found on all scraped transparency portals.

**analyze-links**: Analyzes the transparency portals found by sample URL discovery and attempts to categorize them. Some amount of manual inspection is needed to verify results.

**analyze-discovery**: More analysis of transparency portals found by the URL discovery process. Tries to detect issues like duplicate mappings and compares findings to sample.

