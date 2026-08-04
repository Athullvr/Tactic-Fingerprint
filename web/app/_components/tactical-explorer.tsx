"use client";

import { useEffect, useMemo, useState } from "react";

const FEATURES = ["possession_share", "avg_pass_length", "forward_pass_ratio", "long_pass_ratio", "avg_action_height", "width_dispersion"];
const LABELS: Record<string, string> = { possession_share: "Possession", avg_pass_length: "Pass length", forward_pass_ratio: "Forward passes", long_pass_ratio: "Long passes", avg_action_height: "Defensive height", width_dispersion: "Width" };
type Signature = Record<string, number | string>;
type Profile = { id: string; team: string; competition: string; season: string; signature: Signature; zones: { length: number; width: number; value: number }[]; similar: { team: string; similarity: number }[] };
type Source = { competition: string; season: string };
type Dataset = { sources?: Source[]; teams: Profile[] };

function metric(signature: Signature, key: string) { return Number(signature[`${key}_mean`] ?? signature[key] ?? 0); }
function sourceKey(source: Source) { return `${source.competition}|${source.season}`; }
function percent(value: number) { return `${Math.round(value * 100)}%`; }

function Radar({ left, right }: { left: Profile; right?: Profile }) {
  const values = (profile: Profile) => FEATURES.map((key) => metric(profile.signature, key));
  const normalise = (raw: number[]) => raw.map((value, index) => value / Math.max(...[...values(left), ...(right ? values(right) : [])].map((row) => Math.abs(row)), 0.001));
  const polygon = (points: number[]) => points.map((value, index) => { const angle = -Math.PI / 2 + index * (Math.PI * 2 / FEATURES.length); return `${50 + Math.cos(angle) * value * 39},${50 + Math.sin(angle) * value * 39}`; }).join(" ");
  return <div className="radar-wrap"><svg viewBox="0 0 100 100" role="img" aria-label="Tactical radar chart">{[.25, .5, .75, 1].map((radius) => <circle key={radius} cx="50" cy="50" r={39 * radius} fill="none" stroke="rgba(255,255,255,.12)" />)}{FEATURES.map((feature, index) => { const angle = -Math.PI / 2 + index * (Math.PI * 2 / FEATURES.length); return <text key={feature} x={50 + Math.cos(angle) * 48} y={51 + Math.sin(angle) * 48} textAnchor="middle">{LABELS[feature]}</text>; })}<polygon points={polygon(normalise(values(left)))} className="radar-a" />{right && <polygon points={polygon(normalise(values(right)))} className="radar-b" />}</svg><div className="legend"><span className="dot a" />{left.team}{right && <><span className="dot b" />{right.team}</>}</div></div>;
}

function Pitch({ zones }: { zones: Profile["zones"] }) {
  const max = Math.max(...zones.map((zone) => zone.value), .001);
  return <div className="pitch" aria-label="Territorial action distribution">{zones.map((zone) => <div key={`${zone.length}-${zone.width}`} className="zone" style={{ opacity: .13 + .87 * zone.value / max }} title={`${(zone.value * 100).toFixed(1)}% action share`} />)}</div>;
}

function Summary({ profile, peers }: { profile: Profile; peers: Profile[] }) {
  const direct = metric(profile.signature, "long_pass_ratio"); const height = metric(profile.signature, "avg_action_height"); const possession = metric(profile.signature, "possession_share");
  const style = direct > .35 ? "Direct progression" : possession > .55 ? "Possession control" : height > .6 ? "High territorial pressure" : "Balanced tactical profile";
  const rank = (key: string) => peers.length < 2 ? null : Math.round(100 * peers.filter((item) => metric(item.signature, key) <= metric(profile.signature, key)).length / peers.length);
  const possessionRank = rank("possession_share"); const directRank = rank("long_pass_ratio");
  return <div className="style-card"><span className="eyebrow">Tactical read</span><h3>{style}</h3><p>{possessionRank === null ? "Add more profiles to unlock peer percentiles." : `Possession is higher than ${possessionRank}% of this dataset; directness is higher than ${directRank}% of peers.`}</p></div>;
}

function InsightCards({ profile, peers }: { profile: Profile; peers: Profile[] }) {
  const cards = [
    ["Possession", "possession_share", percent(metric(profile.signature, "possession_share"))],
    ["Pass length", "avg_pass_length", `${metric(profile.signature, "avg_pass_length").toFixed(1)} m`],
    ["Forward intent", "forward_pass_ratio", percent(metric(profile.signature, "forward_pass_ratio"))],
    ["Defensive height", "avg_action_height", percent(metric(profile.signature, "avg_action_height"))],
  ];
  return <section className="insights" aria-label="Key tactical metrics">{cards.map(([label, key, value]) => { const current = metric(profile.signature, key); const rank = peers.length > 1 ? Math.round(100 * peers.filter((item) => metric(item.signature, key) <= current).length / peers.length) : 0; return <article key={key}><span>{label}</span><strong>{value}</strong><small>{peers.length > 1 ? `${rank}th percentile in this source` : "More teams unlock rankings"}</small></article>; })}</section>;
}

export function TacticalExplorer() {
  const [dataset, setDataset] = useState<Dataset | null>(null); const [source, setSource] = useState(""); const [selected, setSelected] = useState(""); const [comparison, setComparison] = useState(""); const [error, setError] = useState("");
  useEffect(() => { fetch("/data/tactical.json").then((response) => response.ok ? response.json() : Promise.reject()).then((payload: Dataset) => { const teams = payload.teams.map((item) => { const competition = item.competition ?? "Champions League"; const season = item.season ?? "2015"; return { ...item, competition, season, id: item.id ?? `${competition}|${season}|${item.team}` }; }); const sources = payload.sources?.length ? payload.sources : [...new Map(teams.map((item) => [sourceKey(item), { competition: item.competition, season: item.season }])).values()]; setDataset({ ...payload, teams, sources }); setSource(sourceKey(sources[0])); }).catch(() => setError("No deployable tactical dataset yet. Run scripts/build_explorer_dataset.py.")); }, []);
  const sources = useMemo(() => dataset?.sources?.length ? dataset.sources : [{ competition: "StatsBomb Open Data", season: "" }], [dataset]);
  const profiles = useMemo(() => dataset?.teams.filter((item) => `${item.competition}|${item.season}` === source) ?? [], [dataset, source]);
  useEffect(() => { setSelected(profiles[0]?.id ?? ""); setComparison(""); }, [source, profiles]);
  const profile = profiles.find((item) => item.id === selected) ?? null; const comparisonProfile = profiles.find((item) => item.id === comparison) ?? null; const alternatives = profiles.filter((item) => item.id !== selected);
  return <>
    <section className="hero"><div><span className="eyebrow">Football style intelligence</span><h1>Every team leaves a<br /><em>tactical fingerprint.</em></h1><p>Explore how teams occupy space, progress the ball, and defend—without reducing football to scorelines.</p></div><div className="hero-stat"><span>{profiles.length || "—"}</span><small>team profiles<br />in this source</small></div></section>
    <section className="controls"><label>Dataset<select value={source} onChange={(event) => setSource(event.target.value)}>{sources.map((item) => <option key={sourceKey(item)} value={sourceKey(item)}>{item.competition} {item.season}</option>)}</select></label><label>Team<select value={selected} onChange={(event) => setSelected(event.target.value)}>{profiles.map((item) => <option key={item.id} value={item.id}>{item.team}</option>)}</select></label><label>Compare with<select value={comparison} onChange={(event) => setComparison(event.target.value)}><option value="">No comparison</option>{alternatives.map((item) => <option key={item.id} value={item.id}>{item.team}</option>)}</select></label><a href="#methodology">Methodology ↓</a></section>
    {error && <p className="notice">{error}</p>}
    {profile && <><InsightCards profile={profile} peers={profiles} /><section className="grid"><div className="panel profile"><div><span className="eyebrow">{profile.competition} · {profile.season}</span><h2>{profile.team} DNA</h2></div><Radar left={profile} right={comparisonProfile ?? undefined} /></div><div className="panel"><span className="eyebrow">Territorial footprint</span><h2>Where actions happen</h2><Pitch zones={profile.zones} /></div><Summary profile={profile} peers={profiles} /><div className="panel similar"><span className="eyebrow">Nearest neighbours</span><h2>Most similar styles</h2>{profile.similar.length ? profile.similar.slice(0, 4).map((item, index) => <button key={`${item.team}-${index}`} onClick={() => { const match = profiles.find((candidate) => candidate.team === item.team); if (match) setSelected(match.id); }}><span>0{index + 1}</span>{item.team}<strong>{Math.max(0, Math.round(item.similarity * 100))}%</strong></button>) : <p>More teams are needed to build a similarity ranking.</p>}</div></section></>}
    <section className="method" id="methodology"><span className="eyebrow">How to read it</span><h2>Not a prediction. A portrait of how a team plays.</h2><div><p><b>Possession & progression</b> measures pass length, forward intent, and circulation.</p><p><b>Territory</b> maps passes, carries, pressures, and recoveries across 30 pitch zones.</p><p><b>Style intelligence</b> standardises profiles for similarity and peer percentiles.</p></div></section>
  </>;
}
