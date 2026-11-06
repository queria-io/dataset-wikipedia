-- 上位の表は 1 日 1,000 行。足りない日があれば止める
select date, count(*) as n
from {{ ref('daily_top') }}
group by date
having count(*) <> 1000
