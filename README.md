# Capacity Forecasting Template

Compare forecast demand hours with team capacity per tower, then output the FTE gap, the number of hires needed, and the latest month a hire must start given recruiting lead time.

## Problem
Staffing decisions get made on gut feel or on average utilization, which hides month-specific peaks. By the time a manager sees a tower at 140% utilization, the hiring lead time has already made it too late to fix.

## Approach
- `demand.csv`: forecast demand hours per tower per month (from your project plan or ticket trend).
- `team.csv`: current FTE, productive hours per FTE per month, target utilization, hiring lead time.
- Core logic, per tower and month:

$$\text{FTE required} = \frac{\text{demand hours}}{\text{productive hours per FTE} \times \text{target utilization}}$$

$$\text{hires needed} = \max\left(0,\ \lceil \text{FTE required} - \text{current FTE} \rceil\right)$$

- `hire_by` = demand month minus hiring lead time. Dates already in the past are flagged `hire_by_overdue`.
- Status: `OK` up to 85% utilization, `AT_RISK` up to 100%, `OVER` above 100%.

## Run it
```bash
pip install pandas
python forecast.py --as-of 2026-11
```

## Measured result (synthetic demo data)
| Tower | Peak utilization | Hires needed at peak | Earliest hire-by |
|---|---|---|---|
| Tower A | 160.7% | 4 | 2026-10 (overdue) |
| Tower B | 104.8% | 1 | 2026-10 (overdue) |
| Tower C | 145.2% | 3 | 2026-11 |

The demo shows the point of the tool: with a 2-month lead time, all three towers already have an overdue hire-by date. An average-utilization view would not have shown this. The figures are generated for illustration, not real team data.

**Your real-world result (fill in after running on your own plan):**
| Metric | Value |
|---|---|
| Towers analysed | _ |
| Hires flagged vs. actual hires made | _ |
| Months of advance warning gained | _ |

## Limitations
- Hires needed is a per-month peak, not additive across months.
- No attrition, leave, ramp-up time, or contractor mix. Add these before using output for headcount approval.
- Output is only as good as the demand forecast. Garbage in, garbage out.

Created by Avash Mohanty, 2026
