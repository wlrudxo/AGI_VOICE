import { W as attr_class, Y as attr, X as ensure_array_like, a0 as clsx } from "../../../../chunks/index2.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { c as carmakerStore } from "../../../../chunks/carmakerStore.svelte.js";
import { t as triggerMonitor } from "../../../../chunks/triggerMonitor.svelte.js";
import { H as HelpModal } from "../../../../chunks/HelpModal.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const signalDefinitions = [
      ["Time", "Simulation Time (s)"],
      ["DM.Gas", "Gas Pedal (0-1)"],
      ["DM.Brake", "Brake Pedal (0-1)"],
      ["DM.Steer.Ang", "Steering Angle (rad)"],
      ["DM.GearNo", "Gear Number"],
      ["Car.v", "Vehicle Speed (m/s)"],
      ["Vhcl.YawRate", "Yaw Rate (rad/s)"],
      ["Vhcl.Steer.Ang", "Wheel Steering Angle (rad)"],
      ["Vhcl.sRoad", "Road Position S (m)"],
      ["Vhcl.tRoad", "Lateral Position T (m)"],
      ["DM.v.Trgt", "Target Speed (m/s)"],
      ["DM.LaneOffset", "Lane Offset (m)"],
      ["Car.tx", "Ego Position X (m)"],
      ["Car.ty", "Ego Position Y (m)"],
      ["LongCtrl.AEB.IsActive", "AEB Active (Braking)"],
      ["Traffic.nObjs", "Active Traffic Objects Count"]
    ];
    const trafficDescMap = {
      "tx": "Position X (m)",
      "ty": "Position Y (m)",
      "v_0.x": "Velocity X (m/s)",
      "v_0.y": "Velocity Y (m/s)",
      "LongVel": "Long Velocity (m/s)",
      "sRoad": "Road Pos S (m)",
      "tRoad": "Lateral Pos T (m)"
    };
    function getDescription(key) {
      const baseSignal = signalDefinitions.find(([signal]) => signal === key);
      if (baseSignal) {
        return baseSignal[1];
      }
      if (key.startsWith("Traffic.T")) {
        const withoutPrefix = key.substring(8);
        const parts = withoutPrefix.split(".", 2);
        if (parts.length === 2) {
          const objName = parts[0];
          const qty = parts[1];
          const desc = trafficDescMap[qty];
          if (desc) {
            return `Traffic ${objName} ${desc}`;
          }
        }
      }
      return "";
    }
    const allSignals = () => {
      const signals = [...signalDefinitions];
      const trafficKeys = Object.keys(carmakerStore.monitorData).filter((key) => key.startsWith("Traffic.T")).sort();
      for (const key of trafficKeys) {
        const desc = getDescription(key);
        if (desc) {
          signals.push([key, desc]);
        }
      }
      return signals;
    };
    let showHelpModal = false;
    let trafficObjectInput = "";
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="vehicle-control svelte-1gmglxi"><div class="page-header"><div class="title-row svelte-1gmglxi"><h1>차량 제어</h1> <button class="btn-icon help-btn">`);
      Icon($$renderer3, {
        icon: "solar:question-circle-bold",
        width: "20",
        height: "20"
      });
      $$renderer3.push(`<!----></button></div> <p class="page-description">CarMaker 차량을 실시간으로 제어합니다.</p></div> <section class="card section"><h2 class="section-title text-primary">Simulation Control</h2> <div class="control-buttons svelte-1gmglxi">`);
      if (carmakerStore.isConnected) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<button class="btn-danger btn-compact">`);
        Icon($$renderer3, { icon: "solar:link-broken-bold", width: "16", height: "16" });
        $$renderer3.push(`<!----> Disconnect</button>`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<button class="btn-primary btn-compact">`);
        Icon($$renderer3, { icon: "solar:link-circle-bold", width: "16", height: "16" });
        $$renderer3.push(`<!----> Connect</button>`);
      }
      $$renderer3.push(`<!--]--> <button${attr_class("btn-compact", void 0, {
        "btn-danger": carmakerStore.isMonitoring,
        "btn-primary": !carmakerStore.isMonitoring
      })}${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, {
        icon: carmakerStore.isMonitoring ? "solar:stop-bold" : "solar:monitoring-bold",
        width: "16",
        height: "16"
      });
      $$renderer3.push(`<!----> ${escape_html(carmakerStore.isMonitoring ? "Stop Monitor" : "Start Monitor")}</button> <button${attr_class("btn-compact trigger-btn", void 0, {
        "btn-danger": triggerMonitor.isMonitoring,
        "btn-primary": !triggerMonitor.isMonitoring
      })}${attr("disabled", !carmakerStore.isConnected || !carmakerStore.isMonitoring, true)}>`);
      Icon($$renderer3, {
        icon: triggerMonitor.isMonitoring ? "solar:stop-bold" : "solar:bolt-bold",
        width: "16",
        height: "16"
      });
      $$renderer3.push(`<!----> `);
      if (triggerMonitor.isMonitoring) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`${escape_html(triggerMonitor.triggers.filter((t) => t.isActive).length)} triggered`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`Start Trigger`);
      }
      $$renderer3.push(`<!--]--></button> <button class="btn-compact btn-secondary"${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, { icon: "solar:restart-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Reset Control</button></div> <div class="control-buttons svelte-1gmglxi"><button class="btn-primary btn-compact"${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, { icon: "solar:play-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Start</button> <button class="btn-danger btn-compact"${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, { icon: "solar:stop-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Stop</button> <button class="btn-secondary btn-compact"${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, { icon: "solar:pause-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Pause (0.001x)</button> <button class="btn-secondary btn-compact"${attr("disabled", !carmakerStore.isConnected, true)}>`);
      Icon($$renderer3, { icon: "solar:restart-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Resume (1.0x)</button></div></section> <section class="card section"><div class="section-header"><h2 class="section-title text-primary">Vehicle Data Monitor</h2></div> <div class="traffic-watch-section svelte-1gmglxi"><div class="traffic-input-row svelte-1gmglxi"><input type="text" class="input-field traffic-input svelte-1gmglxi" placeholder="T00 or 0"${attr("value", trafficObjectInput)}/> <button class="btn-primary btn-compact">`);
      Icon($$renderer3, { icon: "solar:add-circle-bold", width: "16", height: "16" });
      $$renderer3.push(`<!----> Add</button> `);
      if (carmakerStore.watchedTrafficObjects.length > 0) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<button class="btn-secondary btn-compact">`);
        Icon($$renderer3, {
          icon: "solar:trash-bin-trash-bold",
          width: "16",
          height: "16"
        });
        $$renderer3.push(`<!----> Clear All</button>`);
      } else {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></div> `);
      if (carmakerStore.watchedTrafficObjects.length > 0) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="traffic-chips svelte-1gmglxi"><!--[-->`);
        const each_array = ensure_array_like(carmakerStore.watchedTrafficObjects);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let index = each_array[$$index];
          $$renderer3.push(`<span class="traffic-chip svelte-1gmglxi">T${escape_html(index.toString().padStart(2, "0"))} <button class="chip-remove svelte-1gmglxi">`);
          Icon($$renderer3, { icon: "solar:close-circle-bold", width: "14", height: "14" });
          $$renderer3.push(`<!----></button></span>`);
        }
        $$renderer3.push(`<!--]--></div>`);
      } else {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></div> <div class="table-wrapper" style="max-height: 600px; overflow-y: auto;"><table class="table monitor-table svelte-1gmglxi"><thead><tr><th class="svelte-1gmglxi">Variable</th><th class="svelte-1gmglxi">Value</th><th class="svelte-1gmglxi">Description</th></tr></thead><tbody><!--[-->`);
      const each_array_1 = ensure_array_like(allSignals());
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let [signal, desc] = each_array_1[$$index_1];
        const value = carmakerStore.monitorData[signal];
        $$renderer3.push(`<tr><td class="text-primary svelte-1gmglxi">${escape_html(signal)}</td><td${attr_class(clsx(value !== void 0 ? "text-accent" : "text-muted"), "svelte-1gmglxi")}>${escape_html(value !== void 0 && typeof value === "number" ? value.toFixed(4) : "N/A")}</td><td class="text-secondary svelte-1gmglxi">${escape_html(desc)}</td></tr>`);
      }
      $$renderer3.push(`<!--]--></tbody></table></div></section> <section class="card section"><div class="section-header"><h2 class="section-title text-primary">System Log</h2> <button class="btn-text">`);
      Icon($$renderer3, {
        icon: "solar:trash-bin-trash-bold",
        width: "16",
        height: "16"
      });
      $$renderer3.push(`<!----> Clear All</button></div> <div class="log-container">`);
      if (carmakerStore.logMessages.length === 0 && triggerMonitor.logMessages.length === 0) {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<p class="text-muted">No logs yet...</p>`);
      } else {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<!--[-->`);
        const each_array_2 = ensure_array_like(carmakerStore.logMessages);
        for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
          let message = each_array_2[$$index_2];
          $$renderer3.push(`<div class="log-message text-secondary">${escape_html(message)}</div>`);
        }
        $$renderer3.push(`<!--]--> <!--[-->`);
        const each_array_3 = ensure_array_like(triggerMonitor.logMessages);
        for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
          let message = each_array_3[$$index_3];
          $$renderer3.push(`<div class="log-message text-secondary">${escape_html(message)}</div>`);
        }
        $$renderer3.push(`<!--]-->`);
      }
      $$renderer3.push(`<!--]--></div></section></div> `);
      HelpModal($$renderer3, {
        title: "차량 제어 도움말",
        onClose: () => showHelpModal = false,
        get visible() {
          return showHelpModal;
        },
        set visible($$value) {
          showHelpModal = $$value;
          $$settled = false;
        },
        children: ($$renderer4) => {
          $$renderer4.push(`<section class="help-section"><h4>🚗 차량 제어란?</h4> <p class="help-desc">CarMaker 시뮬레이션 환경에서 차량을 실시간으로 제어하고 모니터링하는 시스템입니다. TCP 연결을 통해 차량 데이터를 수신하고 제어 명령을 전송합니다.</p></section> <section class="help-section"><h4>🔌 연결 및 모니터링 버튼</h4> <div class="button-card"><h5>Connect / Disconnect</h5> <p>CarMaker TCP 서버에 연결하거나 연결을 해제합니다.<br/> • <strong>Connect</strong>: TCP 연결 시작 (기본 포트: 16660)<br/> • <strong>Disconnect</strong>: 연결 해제 및 모든 모니터링 중지</p></div> <div class="button-card"><h5>Start Monitor / Stop Monitor</h5> <p>차량 데이터 모니터링을 시작하거나 중지합니다.<br/> • <strong>Start Monitor</strong>: Vehicle Data Monitor 활성화 (10Hz 폴링)<br/> • <strong>Stop Monitor</strong>: 데이터 수신 중지<br/> • 트리거 모니터링을 사용하려면 반드시 먼저 활성화해야 합니다.</p></div> <div class="button-card"><h5>Start Trigger / {n} triggered</h5> <p>트리거 모니터링을 시작하거나 중지합니다.<br/> • <strong>Start Trigger</strong>: 트리거 조건 감지 시작<br/> • <strong>{n} triggered</strong>: 활성화된 트리거 개수 표시 (클릭 시 중지)<br/> • Start Monitor가 활성화되어 있어야 사용 가능합니다.</p></div> <div class="button-card"><h5>Reset Control</h5> <p>모든 차량 제어 명령을 초기화합니다.<br/> • DM.Gas, DM.Brake, DM.Steer.Ang를 0으로 리셋<br/> • 실행 중인 wait_until 및 AI 스크립트 중단<br/> • DM.v.Trgt (목표 속도), DM.LaneOffset (차선 오프셋) 리셋</p></div></section> <section class="help-section"><h4>⚙️ 시뮬레이션 제어 버튼</h4> <div class="button-card"><h5>Start</h5> <p>CarMaker 시뮬레이션을 시작합니다.<br/> • TestRun 실행 시작<br/> • 차량 및 환경 초기화</p></div> <div class="button-card"><h5>Stop</h5> <p>실행 중인 시뮬레이션을 중지합니다.<br/> • TestRun 종료<br/> • 모든 차량 데이터 초기화</p></div> <div class="button-card"><h5>Pause (0.001x)</h5> <p>시뮬레이션을 초감속합니다.<br/> • 시간 스케일을 0.001x로 설정 (사실상 일시정지)<br/> • 차량 모니터링이 활성화된 경우 자동으로 중지됩니다.</p></div> <div class="button-card"><h5>Resume (1.0x)</h5> <p>시뮬레이션을 정상 속도로 복원합니다.<br/> • 시간 스케일을 1.0x로 설정<br/> • Pause 전에 모니터링이 활성화되어 있었다면 자동으로 재시작됩니다.</p></div></section> <section class="help-section"><h4>📊 Vehicle Data Monitor</h4> <p class="help-desc">실시간으로 차량의 상태를 모니터링합니다. Start Monitor 버튼을 클릭하면 10Hz(100ms) 주기로 데이터가 업데이트됩니다.</p> <div class="monitor-categories"><h5>주요 모니터링 데이터:</h5> <ul class="help-list"><li><strong>Time</strong>: 시뮬레이션 시간 (초)</li> <li><strong>DM.Gas, DM.Brake, DM.Steer.Ang</strong>: 가스/브레이크/조향 제어 입력</li> <li><strong>Car.v</strong>: 차량 속도 (m/s)</li> <li><strong>Vhcl.sRoad, Vhcl.tRoad</strong>: 도로 상의 위치 (종방향/횡방향)</li> <li><strong>DM.v.Trgt, DM.LaneOffset</strong>: 목표 속도 및 차선 오프셋</li> <li><strong>Traffic.nObjs</strong>: 활성 교통 객체 수</li> <li><strong>Traffic.T00.*, Traffic.T01.*</strong>: 교통 객체별 위치, 속도 등</li></ul></div></section> <section class="help-section"><h4>📋 System Log</h4> <p class="help-desc">모든 시스템 동작과 명령 실행 결과를 시간순으로 표시합니다.<br/> • CarMaker 명령 실행 로그<br/> • 트리거 발동 로그<br/> • AI 응답 및 차량 제어 명령 실행 로그<br/> • Clear All 버튼으로 로그 삭제 가능</p></section> <section class="help-section"><h4>💡 사용 순서</h4> <ol class="help-list"><li><strong>Connect</strong>: CarMaker TCP 연결</li> <li><strong>Start</strong>: 시뮬레이션 시작</li> <li><strong>Start Monitor</strong>: 차량 데이터 모니터링 활성화</li> <li><strong>Start Trigger</strong>: (선택) 트리거 자동 감지 시작</li> <li>트리거 발동 시 자동으로 Pause → AI 응답 → Resume → 명령 실행</li> <li>필요 시 <strong>Reset Control</strong>로 제어 초기화</li> <li><strong>Stop</strong>: 시뮬레이션 종료</li> <li><strong>Disconnect</strong>: 연결 해제</li></ol></section>`);
        },
        $$slots: { default: true }
      });
      $$renderer3.push(`<!---->`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};
