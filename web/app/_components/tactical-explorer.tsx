"use client";

import { useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const FEATURES = ["possession_share", "avg_pass_length", "forward_pass_ratio", "long_pass_ratio", "avg_action_height", "width_dispersion"];
const LABELS: Record<string, string> = { possession_share: "Possession", avg_pass_length: "Pass length", forward_pass_ratio: "Forward passes", long_pass_ratio: "Long passes", avg_action_height: "Defensive height", width_dispersion: "Width" };
type Signature = Record<string, number | string>;
type Profile = { team: string; signature: Signature; zones: { length: number; width: number; value: number }[]; similar: { team: string; similarity: number }[] };

function metric(signature: Signature, key: string) { return Number(signature[`${key}_mean`] ?? signature[key] ?? 0); }

function Radar({ left, right }: { left: Profile; right?: Profile }) {
  const values = (profile: Profile) => FEATURES.map((key) => metric(profile.signature, key));
  const normalise = (raw: number[]) => raw.map((value, index) => value / Math.max(...[...values(left), ...(right ? values(right) : [])].map((row) => Math.abs(row)), 0.001));
  const polygon = (points: number[]) => points.map((value, index) => {
    const angle = -Math.PI / 2 + index * (Math.PI * 2 / FEATURES.length);
    return `${50 + Math.cos(angle) * value * 39},${50 + Math.sin(angle) * value * 39}`;
  }).join(" ");
  return <div className="radar-wrap"><svg viewBox="0 0 100 100" role="img" aria-label="Tactical radar chart">
    {[.25, .5, .75, 1].map((radius) => <circle key={radius} cx="50" cy="50" r={39 * radius} fill="none" stroke="rgba(255,255,255,.12)" />)}
    {FEATURES.map((feature, index) => { const angle = -Math.PI / 2 + index * (Math.PI * 2 / FEATURES.length); return <text key={feature} x={50 + Math.cos(angle) * 48} y={51 + Math.sin(angle) * 48} textAnchor="middle">{LABELS[feature]}</text>; })}
    <polygon points={polygon(normalise(values(left)))} className="radar-a" />
    {right && <polygon points={polygon(normalise(values(right)))} className="radar-b" />}
  </svg><div className="legend"><span className="dot a" />{left.team}{right && <><span className="dot b" />{right.team}</>}</div></div>;
}

function Pitch({ zones }: { zones: Profile["zones"] }) {
  const max = Math.max(...zones.map((zone) => zone.value), .001);
  return <div className="pitch" aria-label="Territorial action distribution">{zones.map((zone) => <div key={`${zone.length}-${zone.width}`} className="zone" style={{ opacity: .13 + .87 * zone.value / max }} title={`${(zone.value * 100).toFixed(1)}% action share`} />)}</div>;
}

function Summary({ profile }: { profile: Profile }) {
  const direct = metric(profile.signature, "long_pass_ratio");
  const height = metric(profile.signature, "avg_action_height");
  const possession = metric(profile.signature, "possession_share");
  const style = direct > .35 ? "Direct progression" : possession > .55 ? "Possession control" : height > .6 ? "High territorial pressure" : "Balanced tactical profile";
  return <div className="style-card"><span className="eyebrow">Tactical read</span><h3>{style}</h3><p>Derived from passing tendencies, territorial action distribution, defensive height, and width.</p></div>;
}

export function TacticalExplorer() {
  const [teams, setTeams] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [comparison, setComparison] = useState("");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [comparisonProfile, setComparisonProfile] = useState<Profile | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { fetch(`${API}/teams`).then((response) => response.ok ? response.json() : Promise.reject()).then((names: string[]) => { setTeams(names); setSelected(names[0] ?? ""); }).catch(() => setError("Analytics API unavailable. Start uvicorn src.api.app:app --port 8000.")); }, []);
  useEffect(() => { if (selected) fetch(`${API}/teams/${encodeURIComponent(selected)}`).then((response) => response.json()).then(setProfile); }, [selected]);
  useEffect(() => { if (comparison) fetch(`${API}/teams/${encodeURIComponent(comparison)}`).then((response) => response.json()).then(setComparisonProfile); else setComparisonProfile(null); }, [comparison]);
  const alternatives = useMemo(() => teams.filter((team) => team !== selected), [teams, selected]);
  return <>
    <section className="hero"><div><span className="eyebrow">Football style intelligence</span><h1>Every team leaves a<br /><em>tactical fingerprint.</em></h1><p>Explore how teams occupy space, progress the ball, and defend—without reducing football to scorelines.</p></div><div className="hero-stat"><span>30</span><small>territorial zones<br />in every profile</small></div></section>
    <section className="controls"><label>Team<select value={selected} onChange={(event) => setSelected(event.target.value)}>{teams.map((team) => <option key={team}>{team}</option>)}</select></label><label>Compare with<select value={comparison} onChange={(event) => setComparison(event.target.value)}><option value="">No comparison</option>{alternatives.map((team) => <option key={team}>{team}</option>)}</select></label><a href="#methodology">Methodology ↓</a></section>
    {error && <p className="notice">{error}</p>}
    {profile && <section className="grid"><div className="panel profile"><div><span className="eyebrow">{profile.team}</span><h2>DNA profile</h2></div><Radar left={profile} right={comparisonProfile ?? undefined} /></div><div className="panel"><span className="eyebrow">Territorial footprint</span><h2>Where actions happen</h2><Pitch zones={profile.zones} /></div><Summary profile={profile} /><div className="panel similar"><span className="eyebrow">Nearest neighbours</span><h2>Most similar styles</h2>{profile.similar.length ? profile.similar.map((item, index) => <button key={item.team} onClick={() => setSelected(item.team)}><span>0{index + 1}</span>{item.team}<strong>{Math.round(item.similarity * 100)}%</strong></button>) : <p>More teams are needed to build a similarity ranking.</p>}</div></section>}
    <section className="method" id="methodology"><span className="eyebrow">How to read it</span><h2>Not a prediction. A portrait of how a team plays.</h2><div><p><b>Possession & progression</b> measures pass length, forward intent, and circulation.</p><p><b>Territory</b> maps passes, carries, pressures, and recoveries across 30 pitch zones.</p><p><b>Style intelligence</b> standardises profiles for similarity, PCA, and clustering.</p></div></section>
  </>;
}
