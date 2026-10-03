# Frozen test error analysis

This report uses the predictions and labels from the 2011-11-01 test snapshot, after the model and protocol were frozen on validation. It does not alter selection. The machine-readable counts and deterministic example IDs are in `reports/test_error_analysis.json`.

| Slice | Evaluated customers | No top-10 overlap | No-hit rate |
| --- | ---: | ---: | ---: |
| All historical customers with a future label | 1,469 | 626 | 42.614% |
| One historical invoice | 209 | 105 | 50.239% |
| Two to five invoices | 464 | 235 | 50.647% |
| More than five invoices | 796 | 286 | 35.930% |

There were 49,463 distinct future customer-product pairs. Of those, 388 (0.784%) were products not available in the pre-cutoff candidate set, so no model could rank them. 21,478 (43.422%) were repeat purchases, supporting the choice to leave previously bought products eligible. The candidate-set coverage check uses future outcomes only in this post hoc analysis, not in the service path.

The JSON report includes one deterministic no-hit example per history cohort and one customer with a future-only product. These examples show observed purchase overlap, not reasons for preference or non-purchase. There are no impression logs or randomized exposure data, so a miss cannot be interpreted as a rejected recommendation. The higher no-hit rates for customers with at most five invoices suggest sparse history is difficult for this ItemCF setup; any change to routing or model choice must be selected on a fresh validation protocol, not tuned to these test errors.