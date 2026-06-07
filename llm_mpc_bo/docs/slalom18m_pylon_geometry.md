# Slalom18m Pylon Geometry Notes

Date: 2026-06-06

## Source TestRun

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO\ICCAS_Slalom18m_Base
/mnt/e/CarMakerProject/AGI/Data/TestRun/LLM_MPC_BO/ICCAS_Slalom18m_Base
```

The pylon layout is encoded in `Road.RL.1.Marker.*` entries with:

```text
Road.RL.1.Marker.N.Type = DrvPylon
Road.RL.1.Marker.N.Param = s t latOffset speed flag width
```

For the current Slalom18m use, the relevant fields are:

```text
s          longitudinal road position
latOffset  lateral gate center offset
width      gate width
```

The actual plotted pylon positions are interpreted as:

```text
x = s
y = latOffset - width / 2
y = latOffset + width / 2
```

## Confirmed Examples

Full-width gate:

```text
Road.RL.1.Marker.6.ID = 34 1
Road.RL.1.Marker.6.Type = DrvPylon
Road.RL.1.Marker.6.Param = 327 0 0 100 1 9
```

Actual pylon positions:

```text
(327, -4.5)
(327,  4.5)
```

Offset gate to negative side:

```text
Road.RL.1.Marker.7.ID = 35 1
Road.RL.1.Marker.7.Type = DrvPylon
Road.RL.1.Marker.7.Param = 336 0 -2.625 100 1 4.75
```

Actual pylon positions:

```text
(336, -5.0)
(336, -0.25)
```

Offset gate to positive side:

```text
Road.RL.1.Marker.9.ID = 37 1
Road.RL.1.Marker.9.Type = DrvPylon
Road.RL.1.Marker.9.Param = 354 0 2.625 100 1 4.75
```

Actual pylon positions:

```text
(354, 0.25)
(354, 5.0)
```

## Important Correction

Do not plot `latOffset` alone as a pylon location. Values such as `(300, 0)`,
`(309, 0)`, and `(318, 2.625)` are gate-center parameters, not sufficient
actual pylon coordinates.

The earlier trajectory plot looked wrong because it plotted gate centers as
pylons. The corrected plot expands every `DrvPylon` marker into two actual
pylon points using `latOffset +/- width/2`.

This interpretation is consistent with pylon-hit positions recorded in the ERG
summary. For example, a hit at `(336, -0.25)` matches:

```text
latOffset = -2.625
width = 4.75
-2.625 + 4.75 / 2 = -0.25
```

## Generated Files

Scripts:

```text
llm_mpc_bo/scripts/extract_slalom_pylons.py
llm_mpc_bo/scripts/plot_mpc_trial.py
```

Processed pylon geometry:

```text
llm_mpc_bo/results/processed/slalom18m_pylons.csv
llm_mpc_bo/results/processed/slalom18m_pylons.json
```

Figures:

```text
llm_mpc_bo/results/experiments/<experiment>/best_trajectory_pylons.png
```
