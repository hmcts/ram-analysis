(function(){
  var NAV = [["Overview", [["Index", "index", true], ["Knowledge graph (OKF)", "graph", false]]], ["Product", [["PRD (RAM Pathfinder)", "prd", false], ["PRD validation report \u2014 2026-06-17 (5/5)", "prd-validation-report-2026-06-17", false], ["PRD validation report \u2014 2026-06-10", "prd-validation-report-2026-06-10", false]]], ["As-is \u2014 JI Architecture Views", [["System Context (as-is)", "asis/system-context", false], ["Components (as-is)", "asis/components", false]]], ["As-is \u2014 JI Analysis Pack", [["Functional modules (as-is)", "architecture/asis/functional-modules", false], ["Data dependencies (as-is)", "architecture/asis/data-dependencies", false], ["Integration dependencies (as-is)", "architecture/asis/integration-dependencies", false]]], ["As-is \u2014 Tribunals / SSCS", [["Tribunal payment templates (as-is)", "architecture/asis/tribunals/sscs/tribunal-payment-templates", false]]], ["As-is \u2014 JI Database Schema", [["Database index", "asis/database/index", false], ["Schema overview", "asis/database/ji_schema_overview", false], ["Judges Profile & Reference", "asis/database/ji_schema_judges-profile", false], ["Working Patterns, Tickets & Stats", "asis/database/ji_schema_judges-patterns", false], ["Absence & Cover Workflow", "asis/database/ji_schema_absence-cover", false], ["Bookings & Sittings", "asis/database/ji_schema_bookings-sittings", false], ["Reference Data", "asis/database/ji_schema_reference-work", false], ["Audit & Cross-cutting", "asis/database/ji_schema_audit-cross-cutting", false], ["Companion reference (triggers, FKs, externals)", "asis/database/ji_schema_companion", false]]], ["To-be \u2014 RAM Pathfinder Architecture", [["Architecture (index)", "architecture", false], ["Architecture summary", "architecture-summary", false]]], ["To-be \u2014 RAM Pathfinder Analysis", [["Function decomposition (as-is capabilities)", "architecture/tobe/analysis/function-decomposition", false]]], ["To-be \u2014 RAM Pathfinder Reference", [["User types", "architecture/tobe/user-types", false], ["Authoritative table ownership", "architecture/tobe/data-tables", false], ["Conventions", "architecture/tobe/conventions", false], ["Repository strategy", "architecture/tobe/repository-strategy", false], ["Repository structure", "architecture/tobe/repo-structure", false], ["Starter template", "architecture/tobe/starter-template", false], ["Functional requirements coverage", "architecture/tobe/functional-requirements-coverage", false], ["Non-functional requirements coverage", "architecture/tobe/non-functional-requirements-coverage", false]]], ["To-be \u2014 RAM Pathfinder Sequence Diagrams", [["Authentication & authorisation", "architecture/tobe/sequence-diagrams/user-authentication-and-authorisation", false], ["JOH onboarding & sitting gen.", "architecture/tobe/sequence-diagrams/joh-onboarding-and-sitting-generation", false], ["Absence \u2192 Reconciliation", "architecture/tobe/sequence-diagrams/absence-to-reconciliation", false], ["Salaried sitting confirmation", "architecture/tobe/sequence-diagrams/salaried-sitting-confirmation", false], ["Payment batch flow", "architecture/tobe/sequence-diagrams/payment-batch-flow", false], ["Itinerary federated read", "architecture/tobe/sequence-diagrams/itinerary-federated-read", false], ["MI Feed & Reports", "architecture/tobe/sequence-diagrams/mi-feed-and-reports-consumption", false], ["Admin maintenance flows", "architecture/tobe/sequence-diagrams/admin-maintenance-flows", false]]], ["To-be \u2014 RAM Pathfinder Open Items", [["Gaps", "architecture/tobe/gaps", false], ["Assumptions", "architecture/tobe/assumptions", false], ["Changelog", "architecture/tobe/changelog", false]]], ["Change Control & Readiness", [["Sprint Change Proposal \u2014 2026-07-09 (RAM-assigned JOH identity; personnel_number \u2192 upstream link)", "sprint-change-proposal-2026-07-09", false], ["Sprint Change Proposal \u2014 2026-07-07 (Gradle vs Maven-format terminology; contract read-only mirror)", "sprint-change-proposal-2026-07-07", false], ["Sprint Change Proposal \u2014 2026-07-06 (shared infra to dedicated repo, CNP)", "sprint-change-proposal-2026-07-06", false], ["Sprint Change Proposal \u2014 2026-06-17 (integrations-first carve-out)", "sprint-change-proposal-2026-06-17", false], ["Sprint Change Proposal \u2014 2026-06-10 (SSCS-first pivot)", "sprint-change-proposal-2026-06-10", false], ["Sprint Change Proposal \u2014 2026-05-15", "sprint-change-proposal-2026-05-15", false], ["Readiness \u2014 2026-05-15 rev2 (superseded by SCP 2026-06-10; SSCS-cohort assessment pending)", "implementation-readiness-report-2026-05-15-rev2", false], ["Readiness \u2014 2026-05-15 rev1 (superseded by rev2)", "implementation-readiness-report-2026-05-15", false], ["Readiness \u2014 2026-05-06 (historical)", "implementation-readiness-report-2026-05-06", false], ["Readiness \u2014 2026-05-05 (historical)", "implementation-readiness-report-2026-05-05", false]]], ["Implementation \u2014 Epics (Foundations)", [["Delivery operating model (control plane \u00b7 context bus \u00b7 execution units)", "architecture/tobe/delivery-operating-model", false], ["Delivery control plane (dispatch graph + traceability ledger)", "delivery/README", false], ["Epics index", "epics/index", false], ["Requirements inventory", "epics/requirements-inventory", false], ["Phase \u00d7 Area framework", "epics/framework", false], ["FR coverage map", "epics/fr-coverage-map", false]]], ["Implementation \u2014 Phase 0 (platform-then-integrations-first; Epic 0.0 added 2026-07-06)", [["Phase 0 overview", "epics/phase-0/index", false], ["Epic 0.0 \u2014 Platform estate provisioned, verifiable, CNP-compliant (5 stories)", "epics/phase-0/epic-0.0-platform-estate-provisioned", false], ["Epic 0.1 \u2014 Upstream JOH/MRD reference data is ingested (4 stories)", "epics/phase-0/epic-0.1-upstream-reference-data-ingested", false], ["Epic 0.2 \u2014 User authenticates (5 stories)", "epics/phase-0/epic-0.2-user-authenticates", false], ["Epic 0.3 \u2014 Reference data read-only API (2 stories)", "epics/phase-0/epic-0.3-reference-data-read-only-api", false], ["Epic 0.4 \u2014 User populations bootstrapped (1 story)", "epics/phase-0/epic-0.4-user-populations-bootstrapped", false], ["Epic 0.5 \u2014 Notification scaffolded (2 stories)", "epics/phase-0/epic-0.5-system-dispatches-emails", false]]]];
  var base = window.__NAV_BASE__ || './';
  var page = window.__PAGE__ || '';
  var root = document.getElementById('nav-root');
  if (!root) return;
  function slug(s){ return s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,''); }
  var h = '<h2 class="site-title"><a href="' + base + 'index.html">RAM Pathfinder Documentation</a></h2>';
  h += '<div class="nav-controls"><button data-nav-action="expand" title="Expand all groups">Expand all</button> <button data-nav-action="collapse" title="Collapse all groups">Collapse all</button></div>';
  NAV.forEach(function(group){
    var name = group[0], items = group[1];
    var isCurrent = items.some(function(it){ return it[1] === page; });
    h += '<details class="nav-group" data-group="' + slug(name) + '"' + (isCurrent ? ' data-current="true" open' : '') + '>';
    h += '<summary>' + name + '</summary><ul>';
    items.forEach(function(it){
      var href = base + it[1] + '.html';
      var cls = (it[1] === page) ? ' class="current"' : '';
      h += '<li><a href="' + href + '"' + cls + '>' + it[0] + '</a></li>';
    });
    h += '</ul></details>';
  });
  root.innerHTML = h;
  // Persist each group's open/closed state; the current page's group stays open on load.
  root.querySelectorAll('details.nav-group').forEach(function(d){
    var key = 'nav-group-' + d.dataset.group;
    if (d.dataset.current !== 'true') {
      var stored = localStorage.getItem(key);
      if (stored === 'open') d.open = true; else if (stored === 'closed') d.open = false;
    }
    d.addEventListener('toggle', function(){ localStorage.setItem(key, d.open ? 'open' : 'closed'); });
  });
  // Preserve the sidebar's scroll position across page navigations.
  // The site is multi-page, so each click reloads the page and re-renders
  // this nav; without this it would reset to the top every time.
  try { var s = sessionStorage.getItem('nav-scroll'); if (s !== null) root.scrollTop = parseInt(s, 10) || 0; } catch (e) {}
  function saveNavScroll(){ try { sessionStorage.setItem('nav-scroll', String(root.scrollTop)); } catch (e) {} }
  root.addEventListener('click', function(e){ if (e.target.closest && e.target.closest('a')) saveNavScroll(); });
  window.addEventListener('pagehide', saveNavScroll);
  // Expand all / Collapse all (sidebar).
  root.querySelectorAll('button[data-nav-action]').forEach(function(b){
    b.addEventListener('click', function(){
      var open = b.dataset.navAction === 'expand';
      root.querySelectorAll('details.nav-group').forEach(function(d){ d.open = open; });
    });
  });
})();
