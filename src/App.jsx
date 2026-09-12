import React, { useState } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";
import {
  Activity, ArrowRight, BarChart3, Boxes, BrainCircuit, CheckCircle2,
  ChevronRight, CircleDot, Database, FileImage, Gauge, GitCompare,
  ImagePlus, Layers3, Menu, Moon, Orbit, PanelLeft, Play, Rocket,
  ScanSearch, Settings as SettingsIcon, ShieldCheck, Sparkles, Sun, Upload, X, Zap
} from "lucide-react";

const nav = [
  { to: "/", label: "Overview", icon: PanelLeft },
  { to: "/correspondence", label: "Correspondence", icon: GitCompare },
  { to: "/datasets", label: "Datasets", icon: Database },
  { to: "/results", label: "Results", icon: BarChart3 },
];

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-orb"><Orbit size={22}/></div>
          <div>
            <div className="brand-name">LUNA<span>•</span></div>
            <div className="brand-sub">Image Correspondence Engine</div>
          </div>
          <button className="icon-btn mobile-close" onClick={() => setMobileOpen(false)}><X size={18}/></button>
        </div>

        <div className="mission-card">
          <div className="mission-top"><span className="live-dot"></span> MISSION READY</div>
          <div className="mission-title">CHANDRAYAAN-2</div>
          <div className="mission-meta">OHRC · TMC · IIRS</div>
        </div>

        <nav className="nav">
          <div className="nav-label">WORKSPACE</div>
          {nav.map(({to, label, icon: Icon}) => (
            <NavLink key={to} to={to} onClick={() => setMobileOpen(false)}
              className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}>
              <Icon size={18}/><span>{label}</span><ChevronRight size={15} className="nav-arrow"/>
            </NavLink>
          ))}
          <div className="nav-label second">SYSTEM</div>
          <NavLink to="/settings" onClick={() => setMobileOpen(false)}
            className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}>
            <SettingsIcon size={18}/><span>Settings</span>
          </NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status"><span className="live-dot"></span><span>Processing core online</span></div>
          <div className="version">LUNA v1.0 · SIH26166</div>
        </div>
      </aside>

      {mobileOpen && <div className="mobile-overlay" onClick={() => setMobileOpen(false)} />}

      <main className="main">
        <header className="topbar">
          <button className="icon-btn mobile-menu" onClick={() => setMobileOpen(true)}><Menu size={20}/></button>
          <div className="breadcrumbs">
            <span>MISSION CONTROL</span><ChevronRight size={14}/><strong>{nav.find(n => n.to === location.pathname)?.label || "Settings"}</strong>
          </div>
          <div className="top-actions">
            <div className="status-pill"><span className="live-dot"></span> Engine online</div>
            <button className="icon-btn"><Moon size={17}/></button>
            <div className="avatar">SK</div>
          </div>
        </header>
        <div className="page-content">{children}</div>
      </main>
    </div>
  );
}

function SectionTitle({ eyebrow, title, desc, action }) {
  return <div className="section-title">
    <div>
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      <h1>{title}</h1>
      {desc && <p>{desc}</p>}
    </div>
    {action}
  </div>
}

function StatCard({ icon: Icon, label, value, detail, trend }) {
  return <div className="stat-card">
    <div className="stat-icon"><Icon size={19}/></div>
    <div className="stat-label">{label}</div>
    <div className="stat-value">{value}</div>
    <div className="stat-detail">{trend && <span className="trend">{trend}</span>} {detail}</div>
  </div>
}

function Overview() {
  return <div>
    <SectionTitle
      eyebrow="LUNAR VISION PIPELINE"
      title="Correspondence control center"
      desc="Register multi-modal Chandrayaan-2 optical imagery under illumination, viewpoint and scale variations."
      action={<NavLink className="primary-btn" to="/correspondence"><Play size={17}/> Start correspondence</NavLink>}
    />

    <div className="hero-grid">
      <div className="hero-panel">
        <div className="hero-glow"></div>
        <div className="hero-content">
          <div className="tag"><Sparkles size={14}/> MULTI-MODAL · SUN-ANGLE · SCALE INVARIANT</div>
          <h2>Align lunar scenes.<br/><span>Measure what changed.</span></h2>
          <p>LUNA combines preprocessing, feature extraction, robust matching, geometric verification and confidence scoring into one visual workflow.</p>
          <div className="hero-actions">
            <NavLink className="primary-btn" to="/correspondence">Launch pipeline <ArrowRight size={17}/></NavLink>
            <NavLink className="ghost-btn" to="/datasets"><Database size={16}/> Explore datasets</NavLink>
          </div>
        </div>
        <div className="orbit-visual">
          <div className="orbit-ring ring-1"></div>
          <div className="orbit-ring ring-2"></div>
          <div className="orbit-ring ring-3"></div>
          <div className="planet"><Moon size={48}/></div>
          <div className="satellite"><Rocket size={18}/></div>
        </div>
      </div>
      <div className="pipeline-card">
        <div className="card-head"><div><span className="eyebrow">LIVE PIPELINE</span><h3>Processing stages</h3></div><Activity size={19}/></div>
        {["Input validation", "Radiometric normalization", "Feature extraction", "Robust correspondence", "Geometric verification"].map((s,i) =>
          <div className="pipeline-row" key={s}>
            <div className={`stage-dot ${i < 3 ? "done" : ""}`}>{i < 3 ? <CheckCircle2 size={13}/> : i+1}</div>
            <span>{s}</span><span className={i < 3 ? "stage-ok" : "stage-pending"}>{i < 3 ? "READY" : "WAITING"}</span>
          </div>
        )}
      </div>
    </div>

    <div className="stats-grid">
      <StatCard icon={ScanSearch} label="Correspondences" value="12,482" trend="+18.4%" detail="vs last run"/>
      <StatCard icon={Gauge} label="Match confidence" value="94.7%" trend="+3.2%" detail="current best"/>
      <StatCard icon={Layers3} label="Modalities" value="03" detail="OHRC · TMC · IIRS"/>
      <StatCard icon={Zap} label="Median runtime" value="8.4s" trend="-21%" detail="per image pair"/>
    </div>

    <div className="lower-grid">
      <div className="panel">
        <div className="card-head"><div><span className="eyebrow">ARCHITECTURE</span><h3>How LUNA works</h3></div><Boxes size={19}/></div>
        <div className="architecture">
          {[
            ["01","INPUT","OHRC / TMC / IIRS",FileImage],
            ["02","NORMALIZE","Sun-angle aware",Sun],
            ["03","EXTRACT","Invariant features",BrainCircuit],
            ["04","MATCH","Robust descriptors",GitCompare],
            ["05","VERIFY","RANSAC + geometry",ShieldCheck],
          ].map(([n,t,d,Icon]) => <div className="arch-node" key={n}>
            <span className="node-no">{n}</span><Icon size={18}/><b>{t}</b><small>{d}</small>
          </div>)}
        </div>
      </div>
      <div className="panel">
        <div className="card-head"><div><span className="eyebrow">RECENT RUNS</span><h3>Latest correspondence jobs</h3></div><NavLink to="/results" className="text-link">View all <ArrowRight size={14}/></NavLink></div>
        <div className="runs">
          {[
            ["OHRC_0421","TMC_0178","94.7%","8.4s"],
            ["OHRC_0418","IIRS_0091","91.2%","11.1s"],
            ["TMC_0162","IIRS_0088","88.6%","7.8s"],
          ].map(r => <div className="run-row" key={r[0]}>
            <div><b>{r[0]}</b><span>↔ {r[1]}</span></div><strong>{r[2]}</strong><small>{r[3]}</small>
          </div>)}
        </div>
      </div>
    </div>
  </div>
}

function DropZone({ label, modality, onFile }) {
  const [file, setFile] = useState(null);
  const handle = e => {
    const f = e.target.files?.[0];
    if (f) { setFile(f); onFile?.(f); }
  };
  return <label className={`dropzone ${file ? "has-file" : ""}`}>
    <input type="file" accept="image/*,.tif,.tiff" onChange={handle}/>
    <div className="upload-icon">{file ? <CheckCircle2 size={24}/> : <Upload size={24}/>}</div>
    <div className="drop-title">{file ? file.name : label}</div>
    <div className="drop-sub">{file ? `${(file.size/1024/1024).toFixed(2)} MB · ready` : `Upload ${modality} optical image · JPG, PNG, TIFF`}</div>
  </label>
}

function Correspondence() {
  const [referenceFile, setReferenceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);

  const [referenceUploaded, setReferenceUploaded] = useState(null);
  const [targetUploaded, setTargetUploaded] = useState(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/datasets/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "File upload failed.");
    }

    return data;
  };

  const handleReferenceFile = async (file) => {
    setReferenceFile(file);
    setError("");
    setMessage("Uploading reference image...");

    try {
      const data = await uploadFile(file);
      setReferenceUploaded(data.filename);
      setMessage("Reference image uploaded successfully.");
    } catch (err) {
      setError(err.message);
      setReferenceUploaded(null);
    }
  };

  const handleTargetFile = async (file) => {
    setTargetFile(file);
    setError("");
    setMessage("Uploading moving image...");

    try {
      const data = await uploadFile(file);
      setTargetUploaded(data.filename);
      setMessage("Moving image uploaded successfully.");
    } catch (err) {
      setError(err.message);
      setTargetUploaded(null);
    }
  };

  const runCorrespondence = async () => {
    setError("");
    setMessage("");

    if (!referenceUploaded || !targetUploaded) {
      setError("Please upload both reference and moving images first.");
      return;
    }

    setLoading(true);
    setMessage("LunaAlgin is processing the image pair...");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/correspondence",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            reference_filename: referenceUploaded,
            target_filename: targetUploaded,
            ratio_threshold: 0.75,
            reprojection_threshold: 5,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Correspondence processing failed.");
      }

      console.log("LunaAlgin result:", data);

      // Save the complete backend result
      localStorage.setItem(
        "lunaAlginResult",
        JSON.stringify(data)
      );

      setMessage(
        `Completed successfully — ${data.geometry?.inlier_ratio ?? 0}% inlier ratio`
      );

      // Open the real results page after processing
      setTimeout(() => {
        window.location.href = "/results";
      }, 500);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <SectionTitle
        eyebrow="CORRESPONDENCE WORKSPACE"
        title="Create a registration job"
        desc="Select a reference and moving image. The backend will estimate a robust geometric transform and confidence score."
      />

      <div className="workspace-grid">
        <div className="panel">
          <div className="card-head">
            <div>
              <span className="eyebrow">STEP 01</span>
              <h3>Image inputs</h3>
            </div>
            <ImagePlus size={19} />
          </div>

          <div className="upload-grid">
            <DropZone
              label="Reference image"
              modality="fixed/reference"
              onFile={handleReferenceFile}
            />

            <DropZone
              label="Moving image"
              modality="moving/source"
              onFile={handleTargetFile}
            />
          </div>

          <div className="form-grid">
            <label>
              <span>Reference modality</span>
              <select>
                <option>OHRC</option>
                <option>TMC</option>
                <option>IIRS</option>
              </select>
            </label>

            <label>
              <span>Moving modality</span>
              <select>
                <option>TMC</option>
                <option>OHRC</option>
                <option>IIRS</option>
              </select>
            </label>

            <label>
              <span>Matching strategy</span>
              <select>
                <option>Hybrid invariant</option>
                <option>Feature-based</option>
                <option>Intensity-based</option>
              </select>
            </label>

            <label>
              <span>Geometric model</span>
              <select>
                <option>Homography</option>
                <option>Affine</option>
                <option>Similarity</option>
              </select>
            </label>
          </div>

          <div className="advanced-row">
            <div>
              <b>Sun-angle compensation</b>
              <small>
                Normalize illumination before feature extraction
              </small>
            </div>
            <div className="toggle on">
              <span></span>
            </div>
          </div>

          <div className="advanced-row">
            <div>
              <b>Scale-aware matching</b>
              <small>
                Use multi-scale feature pyramid
              </small>
            </div>
            <div className="toggle on">
              <span></span>
            </div>
          </div>

          {message && (
            <div className="success-box">
              <CheckCircle2 size={18} />
              <div>
                <b>Status</b>
                <span>{message}</span>
              </div>
            </div>
          )}

          {error && (
            <div className="success-box">
              <X size={18} />
              <div>
                <b>Error</b>
                <span>{error}</span>
              </div>
            </div>
          )}

          <button
            className="primary-btn full"
            onClick={runCorrespondence}
            disabled={loading}
          >
            <Rocket size={17} />

            {loading
              ? "Processing..."
              : "Run correspondence"}
          </button>
        </div>

        <div className="panel">
          <div className="card-head">
            <div>
              <span className="eyebrow">STEP 02</span>
              <h3>Expected output</h3>
            </div>
            <ScanSearch size={19} />
          </div>

          <div className="preview-card">
            <div className="preview-grid"></div>

            <div className="preview-center">
              <GitCompare size={30} />
              <span>
                {loading
                  ? "Processing..."
                  : "Registration preview"}
              </span>
            </div>
          </div>

          <div className="output-list">
            {[
              ["Aligned image", "Geometrically registered output"],
              ["Match points", "Inlier/outlier correspondence map"],
              ["Transform matrix", "Estimated H / affine parameters"],
              ["Confidence score", "Quality + geometric consistency"],
            ].map((x) => (
              <div className="output-item" key={x[0]}>
                <CheckCircle2 size={16} />
                <div>
                  <b>{x[0]}</b>
                  <small>{x[1]}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Datasets() {
  const rows = [
    ["OHRC-0421","OHRC","2048 × 2048","1.8 GB","Available"],
    ["TMC-0178","TMC","4096 × 4096","3.4 GB","Available"],
    ["IIRS-0091","IIRS","1024 × 1024","812 MB","Available"],
    ["OHRC-0418","OHRC","2048 × 2048","1.6 GB","Available"],
  ];
  return <div>
    <SectionTitle eyebrow="DATA CATALOG" title="Mission datasets" desc="Organize reference and moving imagery used by the correspondence engine."
      action={<button className="primary-btn"><Upload size={17}/> Upload dataset</button>}
    />
    <div className="stats-grid">
      <StatCard icon={Database} label="Image pairs" value="1,284" detail="registered"/>
      <StatCard icon={FileImage} label="Total imagery" value="5,812" detail="indexed"/>
      <StatCard icon={Layers3} label="OHRC / TMC / IIRS" value="3" detail="modalities"/>
      <StatCard icon={ShieldCheck} label="Validated" value="98.2%" detail="metadata quality"/>
    </div>
    <div className="panel table-panel">
      <div className="card-head"><div><span className="eyebrow">CATALOG</span><h3>Indexed imagery</h3></div><span className="count">4 shown</span></div>
      <div className="table-wrap"><table><thead><tr><th>Asset ID</th><th>Sensor</th><th>Resolution</th><th>Size</th><th>Status</th></tr></thead><tbody>
        {rows.map(r => <tr key={r[0]}>{r.map((c,i)=><td key={i}>{i===4 ? <span className="status-badge"><span className="live-dot"></span>{c}</span> : c}</td>)}</tr>)}
      </tbody></table></div>
    </div>
  </div>
}

function Results() {
  const [result, setResult] = useState(null);

  React.useEffect(() => {
    const savedResult = localStorage.getItem("lunaAlginResult");

    if (savedResult) {
      try {
        setResult(JSON.parse(savedResult));
      } catch (error) {
        console.error("Failed to load result:", error);
      }
    }
  }, []);

  if (!result) {
    return (
      <div>
        <SectionTitle
          eyebrow="ANALYTICS"
          title="Correspondence results"
          desc="Run a correspondence job first to view real registration analytics."
        />

        <div className="panel">
          <div className="empty-state">
            <ScanSearch size={32} />

            <h3>No correspondence result yet</h3>

            <p>
              Upload a reference and moving image, then run the LunaAlgin
              correspondence pipeline.
            </p>

            <NavLink className="primary-btn" to="/correspondence">
              <Rocket size={17} />
              Start correspondence
            </NavLink>
          </div>
        </div>
      </div>
    );
  }

  const backendUrl = "http://127.0.0.1:8000";

  const alignedImage =
    `${backendUrl}${result.outputs?.aligned_image || ""}`;

  const correspondenceMap =
    `${backendUrl}${result.outputs?.correspondence_map || ""}`;

  const differenceMap =
    `${backendUrl}${result.outputs?.difference_map || ""}`;

  const inlierRatio = result.geometry?.inlier_ratio ?? 0;
  const alignmentScore = result.registration?.alignment_score ?? 0;

  const totalMatches = result.geometry?.total_matches ?? 0;
  const inliers = result.geometry?.inliers ?? 0;
  const outliers = result.geometry?.outliers ?? 0;

  return (
    <div>

      {/* HEADER */}
      <SectionTitle
        eyebrow="ANALYTICS"
        title="Correspondence results"
        desc="Inspect real match quality, geometric consistency and lunar image registration performance."
        action={
          <NavLink className="ghost-btn" to="/correspondence">
            <GitCompare size={16} />
            New correspondence
          </NavLink>
        }
      />

      {/* RUN SUMMARY */}
      <div className="result-hero">

        <div>
          <span className="eyebrow">COMPLETED RUN</span>

          <h2>
            {result.input?.reference}
            <span> ↔ </span>
            {result.input?.target}
          </h2>

          <p>
            Feature extraction · Ratio-test matching · RANSAC homography ·
            Image registration
          </p>

          <small>
            Job ID: {result.job_id}
          </small>
        </div>

        <div className="score">
          {alignmentScore}%
          <small>alignment score</small>
        </div>

      </div>


      {/* REAL METRICS */}
      <div className="stats-grid">

        <StatCard
          icon={ScanSearch}
          label="Reference keypoints"
          value={result.features?.reference_keypoints ?? 0}
          detail="detected"
        />

        <StatCard
          icon={ScanSearch}
          label="Moving keypoints"
          value={result.features?.target_keypoints ?? 0}
          detail="detected"
        />

        <StatCard
          icon={GitCompare}
          label="Good matches"
          value={result.matching?.good_matches ?? 0}
          detail="after ratio test"
        />

        <StatCard
          icon={ShieldCheck}
          label="RANSAC inliers"
          value={inliers}
          trend={`${inlierRatio}%`}
          detail="inlier ratio"
        />

      </div>


      {/* THREE IMAGE COMPARISON */}
      <div className="panel">

        <div className="card-head">

          <div>
            <span className="eyebrow">
              REGISTRATION COMPARISON
            </span>

            <h3>
              Reference → Moving → Aligned
            </h3>
          </div>

          <ScanSearch size={19} />

        </div>


        <div className="image-comparison-grid">

          {/* REFERENCE */}
          <div className="image-card">

            <div className="image-card-header">
              <div>
                <span className="image-index">01</span>
                <b>Reference image</b>
              </div>

              <span className="image-type">
                FIXED
              </span>
            </div>

            <div className="real-image-preview">

              <img
                src={`${backendUrl}/outputs/${result.input?.reference}`}
                alt="Reference lunar image"
              />

            </div>

            <small>
              Original coordinate system
            </small>

          </div>


          {/* MOVING */}
          <div className="image-card">

            <div className="image-card-header">
              <div>
                <span className="image-index">02</span>
                <b>Moving image</b>
              </div>

              <span className="image-type">
                SOURCE
              </span>
            </div>

            <div className="real-image-preview">

              <img
                src={`${backendUrl}/outputs/${result.input?.target}`}
                alt="Moving lunar image"
              />

            </div>

            <small>
              Input image before registration
            </small>

          </div>


          {/* ALIGNED */}
          <div className="image-card">

            <div className="image-card-header">
              <div>
                <span className="image-index">03</span>
                <b>Aligned image</b>
              </div>

              <span className="image-type success">
                REGISTERED
              </span>
            </div>

            <div className="real-image-preview">

              <img
                src={alignedImage}
                alt="Aligned lunar image"
              />

            </div>

            <small>
              Moving image warped to reference coordinates
            </small>

          </div>

        </div>

      </div>


      {/* CORRESPONDENCE + DIFFERENCE */}
      <div className="result-grid">

        <div className="panel">

          <div className="card-head">

            <div>
              <span className="eyebrow">
                CORRESPONDENCE MAP
              </span>

              <h3>
                Verified feature pairs
              </h3>
            </div>

            <CircleDot size={19} />

          </div>

          <div className="large-image-preview">

            <img
              src={correspondenceMap}
              alt="LunaAlgin correspondence map"
            />

          </div>

          <div className="visual-summary">

            <span>
              <b>{totalMatches}</b>
              total matches
            </span>

            <span>
              <b>{inliers}</b>
              inliers
            </span>

            <span>
              <b>{outliers}</b>
              outliers
            </span>

          </div>

        </div>


        <div className="panel">

          <div className="card-head">

            <div>
              <span className="eyebrow">
                DIFFERENCE ANALYSIS
              </span>

              <h3>
                Registration difference
              </h3>
            </div>

            <Activity size={19} />

          </div>

          <div className="large-image-preview">

            <img
              src={differenceMap}
              alt="LunaAlgin difference map"
            />

          </div>

          <div className="visual-summary">

            <span>
              <b>{alignmentScore}%</b>
              alignment score
            </span>

            <span>
              <b>{inlierRatio}%</b>
              geometric confidence
            </span>

          </div>

        </div>

      </div>


      {/* QUALITY BREAKDOWN */}
      <div className="result-grid">

        <div className="panel">

          <div className="card-head">

            <div>
              <span className="eyebrow">
                MATCH QUALITY
              </span>

              <h3>
                Quality breakdown
              </h3>
            </div>

            <Gauge size={19} />

          </div>


          <div className="metric-row">
            <div>
              <span>Good matches</span>
              <b>{result.matching?.good_matches ?? 0}</b>
            </div>

            <small>
              ratio test
            </small>
          </div>


          <div className="metric-row">
            <div>
              <span>RANSAC inliers</span>
              <b>{inliers}</b>
            </div>

            <small>
              {inlierRatio}%
            </small>
          </div>


          <div className="metric-row">
            <div>
              <span>RANSAC outliers</span>
              <b>{outliers}</b>
            </div>

            <small>
              rejected
            </small>
          </div>


          <div className="metric-row">
            <div>
              <span>Average match distance</span>
              <b>
                {result.matching?.average_distance ?? 0}
              </b>
            </div>

            <small>
              descriptor distance
            </small>
          </div>


          <div className="metric-row">
            <div>
              <span>Best match distance</span>
              <b>
                {result.matching?.best_distance ?? 0}
              </b>
            </div>

            <small>
              strongest match
            </small>
          </div>

        </div>


        {/* HOMOGRAPHY */}
        <div className="panel">

          <div className="card-head">

            <div>
              <span className="eyebrow">
                GEOMETRIC MODEL
              </span>

              <h3>
                Homography matrix
              </h3>
            </div>

            <Boxes size={19} />

          </div>


          <div className="matrix-box">

            {result.homography?.map((row, rowIndex) => (

              <div
                className="matrix-row"
                key={rowIndex}
              >

                {row.map((value, colIndex) => (

                  <code key={colIndex}>
                    {Number(value).toFixed(6)}
                  </code>

                ))}

              </div>

            ))}

          </div>


          <div className="matrix-info">

            <span>
              <b>Model</b>
              Homography
            </span>

            <span>
              <b>RANSAC threshold</b>
              5 px
            </span>

            <span>
              <b>Inlier ratio</b>
              {inlierRatio}%
            </span>

          </div>

        </div>

      </div>


      {/* FINAL STATUS */}
      <div className="panel run-summary">

        <div>

          <span className="eyebrow">
            PIPELINE STATUS
          </span>

          <h3>
            Registration completed successfully
          </h3>

          <p>
            {inliers} of {totalMatches} matched feature pairs
            survived geometric verification.
          </p>

        </div>

        <div className="success-indicator">

          <CheckCircle2 size={20} />

          <span>
            {inlierRatio}% verified
          </span>

        </div>

      </div>

    </div>
  );
}

function Settings() {
  return <div>
    <SectionTitle eyebrow="SYSTEM" title="Engine settings" desc="Configure defaults used by the LUNA processing workflow." />
    <div className="panel settings-panel">
      {[
        ["Default detector","SIFT / SuperPoint hybrid","Feature extraction"],
        ["Matcher","FLANN + ratio test","Descriptor matching"],
        ["RANSAC threshold","3.0 px","Geometric verification"],
        ["Output format","PNG + JSON","Artifacts"],
        ["API endpoint","http://localhost:8000","Backend service"],
      ].map(([a,b,c])=><div className="setting-row" key={a}><div><b>{a}</b><small>{c}</small></div><code>{b}</code></div>)}
    </div>
  </div>
}

export default function App() {
  return <Layout><Routes>
    <Route path="/" element={<Overview/>}/>
    <Route path="/correspondence" element={<Correspondence/>}/>
    <Route path="/datasets" element={<Datasets/>}/>
    <Route path="/results" element={<Results/>}/>
    <Route path="/settings" element={<Settings/>}/>
  </Routes></Layout>
}