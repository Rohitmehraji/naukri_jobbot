"""
Main orchestrator for Naukri Job Application Bot.
4-step pipeline: Scrape -> Score -> Filter -> Apply
"""
import asyncio
import logging
from config import CONFIG
from scraper import scrape_jobs, deduplicate_jobs
from scorer import score_job
from applier import NaukriApplier
from logger_setup import setup_logger


async def main():
    """
    Main bot orchestrator.
    Executes the complete job application workflow.
    """
    logger = setup_logger()
    
    logger.info("="*60)
    logger.info("NAUKRI JOB APPLICATION BOT - STARTING")
    logger.info("="*60)
    logger.info(f"Configuration:")
    logger.info(f"  Search Queries: {CONFIG['search_queries']}")
    logger.info(f"  Location: {CONFIG['location']}")
    logger.info(f"  Min Score: {CONFIG['min_score']}")
    logger.info(f"  Max Applications: {CONFIG['max_applications']}")
    logger.info("="*60)
    
    try:
        # ========== STEP 1: SCRAPE JOBS ==========
        logger.info("[STEP 1] SCRAPING JOBS FROM NAUKRI.COM")
        logger.info("-" * 60)
        
        all_jobs = []
        for query in CONFIG["search_queries"]:
            logger.info(f"Searching: '{query}' in {CONFIG['location']}")
            jobs = scrape_jobs(query, CONFIG["location"], pages=2)
            all_jobs.extend(jobs)
            logger.info(f"  Found {len(jobs)} jobs")
        
        # Deduplicate jobs
        unique_jobs = deduplicate_jobs(all_jobs)
        logger.info(f"Total unique jobs scraped: {len(unique_jobs)}")
        logger.info("-" * 60)
        
        if not unique_jobs:
            logger.warning("No jobs found! Exiting.")
            return
        
        # ========== STEP 2: SCORE JOBS ==========
        logger.info("[STEP 2] SCORING JOBS (KEYWORD MATCHING)")
        logger.info("-" * 60)
        
        for job in unique_jobs:
            score, reason = score_job(job["title"], job["description"])
            job["score"] = score
            job["reason"] = reason
        
        logger.info(f"Scoring complete")
        logger.info("-" * 60)
        
        # ========== STEP 3: FILTER JOBS ==========
        logger.info("[STEP 3] FILTERING JOBS BY RELEVANCE")
        logger.info("-" * 60)
        
        # Filter by score
        filtered = [j for j in unique_jobs if j["score"] >= CONFIG["min_score"]]
        
        # Sort by score (highest first)
        filtered.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit to max applications
        filtered = filtered[:CONFIG["max_applications"]]
        
        logger.info(f"Filtered {len(unique_jobs)} → {len(filtered)} jobs (score >= {CONFIG['min_score']})")
        
        # Show top jobs
        logger.info("Top jobs to apply for:")
        for i, job in enumerate(filtered[:5], 1):
            logger.info(f"  {i}. [{job['score']}/100] {job['title']} @ {job['company']}")
            logger.info(f"     {job['reason']}")
        
        if len(filtered) > 5:
            logger.info(f"  ... and {len(filtered) - 5} more")
        
        logger.info("-" * 60)
        
        if not filtered:
            logger.warning("No jobs passed the filter! Adjust min_score or search queries.")
            return
        
        # ========== STEP 4: APPLY TO JOBS ==========
        logger.info("[STEP 4] APPLYING TO JOBS")
        logger.info("-" * 60)
        
        applier = NaukriApplier(CONFIG)
        await applier.run(filtered)
        
        logger.info("-" * 60)
        logger.info("[STEP 5] COMPLETE")
        logger.info("="*60)
        logger.info("Bot execution finished successfully!")
        logger.info("="*60)
    
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        logger.error("Bot execution failed!")


if __name__ == "__main__":
    asyncio.run(main())
