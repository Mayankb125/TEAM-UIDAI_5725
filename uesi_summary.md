# Phase 3.1: UESI Results

![Distribution](d:/UIDAI data hackathon/outputs/figures\uesi_distribution.png)

## Top 10 High-Stress Districts (Score > 90)
```
                    district  Total_Enrolment  Total_Adult_Updates  UESI_Score
                     Thoubal             1019              63473.0       100.0
                    Salumbar                1                147.0       100.0
                  Gadchiroli             2341             136255.0       100.0
                     Balotra                1                353.0       100.0
          Medchal?malkajgiri                2                593.0       100.0
                      Beawar                1                377.0       100.0
                       Deeg                 8                738.0       100.0
            Didwana-Kuchaman                2                485.0       100.0
                 Ahilyanagar               12               1597.0       100.0
Mohla-Manpur-Ambagarh Chouki              253              17286.0       100.0
```

## Metric Logic
- **Why Adult Updates?**: Adults rarely change biometrics (fingers don't grow). Frequent updates imply data errors or address changes.
- **Normalization**: Scores are relative. 100 = The most stressed district in the dataset.
