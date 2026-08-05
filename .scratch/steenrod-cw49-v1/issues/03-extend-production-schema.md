Type: task
Status: resolved
Claimed by: /root/steenrod_schema
Claimed at: 2026-08-05T15:58:08Z
Blocked by: 01

# Extend the production schema

Add append-only migration 0005 for spectra, modules, basis elements, action
assertions, completeness, and Snapshot projection integrity.

## Answer

Migration `0005_stable_steenrod_modules.sql` adds typed spectra, aliases,
finite-basis and profile modules, ordered homogeneous bases, sparse action and
completeness assertions, and Snapshot projections. Rebuilt integrity triggers
extend assertion subjects, knowledge links, and Snapshot records without
changing any earlier migration bytes. Exact empty actions remain zero,
reviewed unknown actions remain distinct from uncovered slots, and the
instability trigger applies only to unstable modules.

Typed import-evidence records bind every normalized module to its source
Snapshot and normalized-module hash. Snapshot admission now requires that
evidence, while the canonical logical `/2` database hash excludes only the
non-semantic migration timestamp and is stable across delayed builds.

## Comments

- Resolved by `/root/steenrod_schema` on 2026-08-05 after 28 focused migration,
  materialization, logical-identity, rollback, and integrity tests passed.
