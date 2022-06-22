--this script is run within the PostgreSQL Server on RDS
--to create a view joining the stores and deals tables.

CREATE VIEW games_savings.dashboard AS 

SELECT d.title,
s.store_name,
d.game_id,
d.sale_price,
d.normal_price,
CASE WHEN d.is_on_sale = 1 THEN 'On Sale' WHEN d.is_on_sale = 0 THEN 'Not on Sale' END AS sale_status,
d.savings,
d.metacritic_score,
d.steam_rating_percent,
d.release_date,
d.last_change,
d.deal_rating,
d.deal_url FROM games_savings.deals d
LEFT JOIN games_savings.stores s
ON d.store_id = s.store_id
;
