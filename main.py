import db
from scp import SCP
import global_vars
import cfg
import scraper
import gui


ORM = db.SCPDatabase(cfg.DB_NAME)
scraper = scraper.WikiScraper()
GUI = gui.TkinterGUI()
GUI.start()
