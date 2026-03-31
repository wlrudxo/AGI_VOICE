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

## 핵심 주의점

- TestRun 수정과 Variation 수정은 구분한다.
- trailer 부착은 parameter set과 key-value override 중 어느 방식인지 분명히 한다.
- project path와 relative dataset path를 항상 명시한다.
