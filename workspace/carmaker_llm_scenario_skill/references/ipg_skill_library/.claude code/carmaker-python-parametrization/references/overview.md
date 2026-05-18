# CarMaker Python Parametrization Reference

## 기준 예제

- `C:\IPG\carmaker\win64-14.0.1\Examples\Python\parametrization_full_example.py`
- `C:\IPG\carmaker\win64-14.0.1\Examples\Python\parametrization_sim_param_example.py`

## 대표 흐름

1. `Project.load(project_path)`
2. TestRun parametrization load
3. vehicle/trailer parametrization load
4. parameter 값 변경
5. `Variation.create_from_testrun(...)` 또는 clone
6. key-value override 적용
