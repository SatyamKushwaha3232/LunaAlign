import React, { useEffect, useState } from "react";
import {
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  Activity,
  ArrowRight,
  BarChart3,
  Boxes,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Database,
  FileImage,
  Gauge,
  GitCompare,
  ImagePlus,
  Layers3,
  Menu,
  Moon,
  Orbit,
  PanelLeft,
  Play,
  Rocket,
  ScanSearch,
  Settings as SettingsIcon,
  ShieldCheck,
  Sparkles,
  Sun,
  Upload,
  X,
  Zap,
} from "lucide-react";

/* =========================================================
   BACKEND CONFIG
========================================================= */

const BACKEND_URL = "http://127.0.0.1:8000";

const API = {
  upload: `${BACKEND_URL}/api/v1/datasets/upload`,
  datasets: `${BACKEND_URL}/api/v1/datasets`,
  correspondence: `${BACKEND_URL}/api/v1/correspondence`,
};

/* =========================================================
   NAVIGATION
========================================================= */

const nav = [
  {
    to: "/",
    label: "Overview",
    icon: PanelLeft,
  },
  {
    to: "/correspondence",
    label: "Correspondence",
    icon: GitCompare,
  },
  {
    to: "/datasets",
    label: "Datasets",
    icon: Database,
  },
  {
    to: "/results",
    label: "Results",
    icon: BarChart3,
  },
];

/* =========================================================
   HELPERS
========================================================= */

function getErrorMessage(data, fallback = "Something went wrong.") {
  if (!data) return fallback;

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => item?.msg || "Validation error")
      .join(", ");
  }

  if (typeof data.message === "string") {
    return data.message;
  }

  return fallback;
}

function getTransformationMatrix(result) {
  if (
    Array.isArray(result?.transformation?.matrix) &&
    result.transformation.matrix.length > 0
  ) {
    return result.transformation.matrix;
  }

  if (
    Array.isArray(result?.homography) &&
    result.homography.length > 0
  ) {
    return result.homography;
  }

  return [];
}

function getTransformationModel(result) {
  return (
    result?.transformation?.model ||
    result?.geometry?.model ||
    "Homography"
  );
}

function formatNumber(value, digits = 4) {
  if (value === null || value === undefined || value === "") {
    return "0";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toFixed(digits);
}

/* =========================================================
   LAYOUT
========================================================= */

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-orb">
            <Orbit size={22} />
          </div>

          <div>
            <div className="brand-name">
              LUNA<span>•</span>
            </div>

            <div className="brand-sub">
              Image Correspondence Engine
            </div>
          </div>

          <button
            className="icon-btn mobile-close"
            onClick={() => setMobileOpen(false)}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mission-card">
          <div className="mission-top">
            <span className="live-dot"></span>
            MISSION READY
          </div>

          <div className="mission-title">
            CHANDRAYAAN-2
          </div>

          <div className="mission-meta">
            OHRC · TMC · IIRS
          </div>
        </div>

        <nav className="nav">
          <div className="nav-label">
            WORKSPACE
          </div>

          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />

              <span>{label}</span>

              <ChevronRight
                size={15}
                className="nav-arrow"
              />
            </NavLink>
          ))}

          <div className="nav-label second">
            SYSTEM
          </div>

          <NavLink
            to="/settings"
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <SettingsIcon size={18} />
            <span>Settings</span>
          </NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="live-dot"></span>
            <span>Processing core online</span>
          </div>

          <div className="version">
            LUNA v1.0 · SIH26166
          </div>
        </div>
      </aside>

      {mobileOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <main className="main">
        <header className="topbar">
          <button
            className="icon-btn mobile-menu"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>

          <div className="breadcrumbs">
            <span>MISSION CONTROL</span>

            <ChevronRight size={14} />

            <strong>
              {nav.find(
                (n) => n.to === location.pathname
              )?.label || "Settings"}
            </strong>
          </div>

          <div className="top-actions">
            <div className="status-pill">
              <span className="live-dot"></span>
              Engine online
            </div>

            <button
              className="icon-btn"
              aria-label="Theme"
            >
              <Moon size={17} />
            </button>

            <div className="avatar">
              SK
            </div>
          </div>
        </header>

        <div className="page-content">
          {children}
        </div>
      </main>
    </div>
  );
}

/* =========================================================
   COMMON COMPONENTS
========================================================= */

function SectionTitle({
  eyebrow,
  title,
  desc,
  action,
}) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && (
          <div className="eyebrow">
            {eyebrow}
          </div>
        )}

        <h1>{title}</h1>

        {desc && <p>{desc}</p>}
      </div>

      {action}
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
  trend,
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">
        <Icon size={19} />
      </div>

      <div className="stat-label">
        {label}
      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-detail">
        {trend && (
          <span className="trend">
            {trend}
          </span>
        )}{" "}
        {detail}
      </div>
    </div>
  );
}

/* =========================================================
   OVERVIEW
========================================================= */

function Overview() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    const savedResult =
      localStorage.getItem("lunaAlginResult");

    if (savedResult) {
      try {
        setResult(JSON.parse(savedResult));
      } catch (error) {
        console.error(
          "Failed to load overview result:",
          error
        );
      }
    }
  }, []);

  const correspondences =
    result?.geometry?.total_matches ?? 0;

  const matchConfidence =
    result?.geometry?.inlier_ratio ?? 0;

  const alignmentScore =
    result?.registration?.alignment_score ?? 0;

  const inliers =
    result?.geometry?.inliers ?? 0;

  const outliers =
    result?.geometry?.outliers ?? 0;

  return (
    <div>
      <SectionTitle
        eyebrow="LUNAR VISION PIPELINE"
        title="Correspondence control center"
        desc="Register multi-modal Chandrayaan-2 optical imagery under illumination, viewpoint and scale variations."
        action={
          <NavLink
            className="primary-btn"
            to="/correspondence"
          >
            <Play size={17} />
            Start correspondence
          </NavLink>
        }
      />

      <div className="hero-grid">
        <div className="hero-panel">
          <div className="hero-glow"></div>

          <div className="hero-content">
            <div className="tag">
              <Sparkles size={14} />
              MULTI-MODAL · SUN-ANGLE · SCALE INVARIANT
            </div>

            <h2>
              Align lunar scenes.
              <br />
              <span>Measure what changed.</span>
            </h2>

            <p>
              LUNA combines preprocessing, feature
              extraction, robust matching, geometric
              verification and confidence scoring into
              one visual workflow.
            </p>

            <div className="hero-actions">
              <NavLink
                className="primary-btn"
                to="/correspondence"
              >
                Launch pipeline
                <ArrowRight size={17} />
              </NavLink>

              <NavLink
                className="ghost-btn"
                to="/datasets"
              >
                <Database size={16} />
                Explore datasets
              </NavLink>
            </div>
          </div>

          <div className="orbit-visual">
            <div className="orbit-ring ring-1"></div>
            <div className="orbit-ring ring-2"></div>
            <div className="orbit-ring ring-3"></div>

            <div className="planet">
              <Moon size={48} />
            </div>

            <div className="satellite">
              <Rocket size={18} />
            </div>
          </div>
        </div>

        <div className="pipeline-card">
          <div className="card-head">
            <div>
              <span className="eyebrow">
                LIVE PIPELINE
              </span>

              <h3>
                Processing stages
              </h3>
            </div>

            <Activity size={19} />
          </div>

          {[
            [
              "Input validation",
              "Dataset accepted",
            ],
            [
              "Radiometric normalization",
              "Illumination compensated",
            ],
            [
              "Feature extraction",
              "Multi-scale SIFT",
            ],
            [
              "Robust correspondence",
              "Ratio-test matching",
            ],
            [
              "Geometric verification",
              "RANSAC homography",
            ],
          ].map(
            ([stage, description], i) => {
              const completed = result
                ? true
                : i < 2;

              return (
                <div
                  className="pipeline-row"
                  key={stage}
                >
                  <div
                    className={`stage-dot ${
                      completed ? "done" : ""
                    }`}
                  >
                    {completed ? (
                      <CheckCircle2 size={13} />
                    ) : (
                      i + 1
                    )}
                  </div>

                  <div>
                    <span>{stage}</span>
                    <small>
                      {description}
                    </small>
                  </div>

                  <span
                    className={
                      completed
                        ? "stage-ok"
                        : "stage-pending"
                    }
                  >
                    {completed
                      ? "COMPLETED"
                      : "WAITING"}
                  </span>
                </div>
              );
            }
          )}
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={ScanSearch}
          label="Correspondences"
          value={correspondences}
          detail={
            result
              ? `${inliers} verified inliers`
              : "run a pair first"
          }
        />

        <StatCard
          icon={Gauge}
          label="Match confidence"
          value={`${matchConfidence}%`}
          detail={
            result
              ? "RANSAC inlier ratio"
              : "awaiting result"
          }
        />

        <StatCard
          icon={Layers3}
          label="Modalities"
          value="03"
          detail="OHRC · TMC · IIRS"
        />

        <StatCard
          icon={Zap}
          label="Alignment score"
          value={`${alignmentScore}%`}
          detail={
            result
              ? `${outliers} rejected outliers`
              : "awaiting result"
          }
        />
      </div>

      <div className="lower-grid">
        <div className="panel">
          <div className="card-head">
            <div>
              <span className="eyebrow">
                ARCHITECTURE
              </span>

              <h3>
                How LUNA works
              </h3>
            </div>

            <Boxes size={19} />
          </div>

          <div className="architecture">
            {[
              [
                "01",
                "INPUT",
                "OHRC / TMC / IIRS",
                FileImage,
              ],
              [
                "02",
                "NORMALIZE",
                "Sun-angle aware",
                Sun,
              ],
              [
                "03",
                "EXTRACT",
                "Invariant features",
                BrainCircuit,
              ],
              [
                "04",
                "MATCH",
                "Robust descriptors",
                GitCompare,
              ],
              [
                "05",
                "VERIFY",
                "RANSAC + geometry",
                ShieldCheck,
              ],
            ].map(
              ([n, t, d, Icon]) => (
                <div
                  className="arch-node"
                  key={n}
                >
                  <span className="node-no">
                    {n}
                  </span>

                  <Icon size={18} />

                  <b>{t}</b>

                  <small>{d}</small>
                </div>
              )
            )}
          </div>
        </div>

        <div className="panel">
          <div className="card-head">
            <div>
              <span className="eyebrow">
                RECENT RUNS
              </span>

              <h3>
                Latest correspondence jobs
              </h3>
            </div>

            <NavLink
              to="/results"
              className="text-link"
            >
              View all
              <ArrowRight size={14} />
            </NavLink>
          </div>

          <div className="runs">
            {result ? (
              <>
                <div className="run-row">
                  <div>
                    <b>
                      {result.input?.reference}
                    </b>

                    <span>
                      ↔ {result.input?.target}
                    </span>
                  </div>

                  <strong>
                    {result.geometry
                      ?.inlier_ratio ?? 0}
                    %
                  </strong>

                  <small>
                    Verified
                  </small>
                </div>

                <div className="run-row">
                  <div>
                    <b>
                      Good matches
                    </b>

                    <span>
                      Ratio-test verified
                    </span>
                  </div>

                  <strong>
                    {result.matching
                      ?.good_matches ?? 0}
                  </strong>

                  <small>
                    Matches
                  </small>
                </div>

                <div className="run-row">
                  <div>
                    <b>
                      Alignment score
                    </b>

                    <span>
                      Registration quality
                    </span>
                  </div>

                  <strong>
                    {result.registration
                      ?.alignment_score ?? 0}
                    %
                  </strong>

                  <small>
                    Score
                  </small>
                </div>
              </>
            ) : (
              <div className="empty-state">
                <ScanSearch size={24} />

                <span>
                  No correspondence run yet.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   DROP ZONE
========================================================= */

function DropZone({
  label,
  modality,
  onFile,
}) {
  const [file, setFile] =
    useState(null);

  const handle = (event) => {
    const selectedFile =
      event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
      onFile?.(selectedFile);
    }
  };

  return (
    <label
      className={`dropzone ${
        file ? "has-file" : ""
      }`}
    >
      <input
        type="file"
        accept="image/*,.tif,.tiff"
        onChange={handle}
      />

      <div className="upload-icon">
        {file ? (
          <CheckCircle2 size={24} />
        ) : (
          <Upload size={24} />
        )}
      </div>

      <div className="drop-title">
        {file
          ? file.name
          : label}
      </div>

      <div className="drop-sub">
        {file
          ? `${(
              file.size /
              1024 /
              1024
            ).toFixed(2)} MB · ready`
          : `Upload ${modality} optical image · JPG, PNG, TIFF`}
      </div>
    </label>
  );
}

/* =========================================================
   CORRESPONDENCE
========================================================= */

function Correspondence() {
  const navigate = useNavigate();

  const [
    referenceFile,
    setReferenceFile,
  ] = useState(null);

  const [
    targetFile,
    setTargetFile,
  ] = useState(null);

  const [
    referenceUploaded,
    setReferenceUploaded,
  ] = useState(null);

  const [
    targetUploaded,
    setTargetUploaded,
  ] = useState(null);

  const [
    referenceModality,
    setReferenceModality,
  ] = useState("OHRC");

  const [
    targetModality,
    setTargetModality,
  ] = useState("TMC");

  const [
    matchingStrategy,
    setMatchingStrategy,
  ] = useState("Hybrid invariant");

  const [
    geometricModel,
    setGeometricModel,
  ] = useState("Homography");

  const [
    sunAngleCompensation,
    setSunAngleCompensation,
  ] = useState(true);

  const [
    scaleAwareMatching,
    setScaleAwareMatching,
  ] = useState(true);

  const [
    ratioThreshold,
    setRatioThreshold,
  ] = useState(0.75);

  const [
    reprojectionThreshold,
    setReprojectionThreshold,
  ] = useState(5);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  /* -------------------------------------------------------
     UPLOAD
  ------------------------------------------------------- */

  const uploadFile = async (file) => {
    if (!file) {
      throw new Error(
        "No file selected."
      );
    }

    const formData =
      new FormData();

    formData.append(
      "file",
      file
    );

    const response =
      await fetch(
        API.upload,
        {
          method: "POST",
          body: formData,
        }
      );

    let data = null;

    try {
      data =
        await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          "File upload failed."
        )
      );
    }

    return data;
  };

  /* -------------------------------------------------------
     REFERENCE UPLOAD
  ------------------------------------------------------- */

  const handleReferenceFile =
    async (file) => {
      setReferenceFile(file);
      setError("");
      setMessage(
        "Uploading reference image..."
      );

      try {
        const data =
          await uploadFile(file);

        setReferenceUploaded(
          data.filename
        );

        setMessage(
          "Reference image uploaded successfully."
        );
      } catch (err) {
        setError(
          err.message ||
            "Reference upload failed."
        );

        setReferenceUploaded(
          null
        );
      }
    };

  /* -------------------------------------------------------
     TARGET UPLOAD
  ------------------------------------------------------- */

  const handleTargetFile =
    async (file) => {
      setTargetFile(file);
      setError("");
      setMessage(
        "Uploading moving image..."
      );

      try {
        const data =
          await uploadFile(file);

        setTargetUploaded(
          data.filename
        );

        setMessage(
          "Moving image uploaded successfully."
        );
      } catch (err) {
        setError(
          err.message ||
            "Moving image upload failed."
        );

        setTargetUploaded(
          null
        );
      }
    };

  /* -------------------------------------------------------
     RUN CORRESPONDENCE
  ------------------------------------------------------- */

  const runCorrespondence =
    async () => {
      setError("");
      setMessage("");

      if (!referenceUploaded) {
        setError(
          "Please upload the reference image first."
        );
        return;
      }

      if (!targetUploaded) {
        setError(
          "Please upload the moving image first."
        );
        return;
      }

      setLoading(true);

      setMessage(
        "LunaAlgin is processing the image pair..."
      );

      try {
        const response =
          await fetch(
            API.correspondence,
            {
              method: "POST",
              headers: {
                "Content-Type":
                  "application/json",
              },
              body: JSON.stringify({
                reference_filename:
                  referenceUploaded,

                target_filename:
                  targetUploaded,

                reference_modality:
                  referenceModality,

                target_modality:
                  targetModality,

                matching_strategy:
                  matchingStrategy,

                geometric_model:
                  geometricModel.toLowerCase(),

                ratio_threshold:
                  Number(
                    ratioThreshold
                  ),

                reprojection_threshold:
                  Number(
                    reprojectionThreshold
                  ),

                sun_angle_compensation:
                  sunAngleCompensation,

                scale_aware_matching:
                  scaleAwareMatching,
              }),
            }
          );

        let data = null;

        try {
          data =
            await response.json();
        } catch {
          data = null;
        }

        if (!response.ok) {
          throw new Error(
            getErrorMessage(
              data,
              "Correspondence processing failed."
            )
          );
        }

        console.log(
          "LunaAlgin result:",
          data
        );

        localStorage.setItem(
          "lunaAlginResult",
          JSON.stringify(data)
        );

        setMessage(
          `Completed successfully — ${
            data.geometry
              ?.inlier_ratio ?? 0
          }% inlier ratio`
        );

        setTimeout(() => {
          navigate("/results");
        }, 500);
      } catch (err) {
        console.error(
          "Correspondence error:",
          err
        );

        setError(
          err.message ||
            "Correspondence processing failed."
        );
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
              <span className="eyebrow">
                STEP 01
              </span>

              <h3>
                Image inputs
              </h3>
            </div>

            <ImagePlus size={19} />
          </div>

          <div className="upload-grid">
            <DropZone
              label="Reference image"
              modality="fixed/reference"
              onFile={
                handleReferenceFile
              }
            />

            <DropZone
              label="Moving image"
              modality="moving/source"
              onFile={
                handleTargetFile
              }
            />
          </div>

          <div className="form-grid">
            <label>
              <span>
                Reference modality
              </span>

              <select
                value={
                  referenceModality
                }
                onChange={(event) =>
                  setReferenceModality(
                    event.target.value
                  )
                }
              >
                <option>
                  OHRC
                </option>

                <option>
                  TMC
                </option>

                <option>
                  IIRS
                </option>
              </select>
            </label>

            <label>
              <span>
                Moving modality
              </span>

              <select
                value={
                  targetModality
                }
                onChange={(event) =>
                  setTargetModality(
                    event.target.value
                  )
                }
              >
                <option>
                  TMC
                </option>

                <option>
                  OHRC
                </option>

                <option>
                  IIRS
                </option>
              </select>
            </label>

            <label>
              <span>
                Matching strategy
              </span>

              <select
                value={
                  matchingStrategy
                }
                onChange={(event) =>
                  setMatchingStrategy(
                    event.target.value
                  )
                }
              >
                <option>
                  Hybrid invariant
                </option>

                <option>
                  Feature-based
                </option>

                <option>
                  Intensity-based
                </option>
              </select>
            </label>

            <label>
              <span>
                Geometric model
              </span>

              <select
                value={
                  geometricModel
                }
                onChange={(event) =>
                  setGeometricModel(
                    event.target.value
                  )
                }
              >
                <option>
                  Homography
                </option>

                <option>
                  Affine
                </option>

                <option>
                  Similarity
                </option>
              </select>
            </label>
          </div>

          <div className="advanced-row">
            <div>
              <b>
                Sun-angle compensation
              </b>

              <small>
                Normalize illumination before feature extraction
              </small>
            </div>

            <button
              type="button"
              className={`toggle ${
                sunAngleCompensation
                  ? "on"
                  : ""
              }`}
              onClick={() =>
                setSunAngleCompensation(
                  (value) => !value
                )
              }
              aria-label="Toggle sun-angle compensation"
            >
              <span></span>
            </button>
          </div>

          <div className="advanced-row">
            <div>
              <b>
                Scale-aware matching
              </b>

              <small>
                Use multi-scale feature pyramid
              </small>
            </div>

            <button
              type="button"
              className={`toggle ${
                scaleAwareMatching
                  ? "on"
                  : ""
              }`}
              onClick={() =>
                setScaleAwareMatching(
                  (value) => !value
                )
              }
              aria-label="Toggle scale-aware matching"
            >
              <span></span>
            </button>
          </div>

          <div className="form-grid">
            <label>
              <span>
                Ratio threshold
              </span>

              <input
                type="number"
                min="0.5"
                max="0.95"
                step="0.01"
                value={
                  ratioThreshold
                }
                onChange={(event) =>
                  setRatioThreshold(
                    event.target.value
                  )
                }
              />
            </label>

            <label>
              <span>
                RANSAC threshold (px)
              </span>

              <input
                type="number"
                min="0.5"
                max="20"
                step="0.5"
                value={
                  reprojectionThreshold
                }
                onChange={(event) =>
                  setReprojectionThreshold(
                    event.target.value
                  )
                }
              />
            </label>
          </div>

          {message && (
            <div className="success-box">
              <CheckCircle2 size={18} />

              <div>
                <b>Status</b>

                <span>
                  {message}
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="success-box">
              <X size={18} />

              <div>
                <b>Error</b>

                <span>
                  {error}
                </span>
              </div>
            </div>
          )}

          <button
            className="primary-btn full"
            onClick={
              runCorrespondence
            }
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
              <span className="eyebrow">
                STEP 02
              </span>

              <h3>
                Expected output
              </h3>
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
              [
                "Aligned image",
                "Geometrically registered output",
              ],
              [
                "Match points",
                "Inlier/outlier correspondence map",
              ],
              [
                "Transform matrix",
                "Estimated H / affine parameters",
              ],
              [
                "Confidence score",
                "Quality + geometric consistency",
              ],
            ].map((x) => (
              <div
                className="output-item"
                key={x[0]}
              >
                <CheckCircle2 size={16} />

                <div>
                  <b>{x[0]}</b>

                  <small>
                    {x[1]}
                  </small>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   DATASETS
========================================================= */

function Datasets() {
  const [datasets, setDatasets] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const loadDatasets =
    async () => {
      setLoading(true);
      setError("");

      try {
        const response =
          await fetch(
            API.datasets
          );

        let data = null;

        try {
          data =
            await response.json();
        } catch {
          data = null;
        }

        if (!response.ok) {
          throw new Error(
            getErrorMessage(
              data,
              "Unable to load datasets."
            )
          );
        }

        setDatasets(
          data?.datasets || []
        );
      } catch (err) {
        setError(
          err.message ||
            "Unable to load datasets."
        );
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    loadDatasets();
  }, []);

  const formatSize =
    (sizeMb) => {
      if (
        sizeMb === null ||
        sizeMb === undefined
      ) {
        return "—";
      }

      const number =
        Number(sizeMb);

      if (Number.isNaN(number)) {
        return "—";
      }

      if (number >= 1024) {
        return `${(
          number / 1024
        ).toFixed(2)} GB`;
      }

      return `${number.toFixed(
        2
      )} MB`;
    };

  const formatResolution =
    (value) => {
      if (
        value === null ||
        value === undefined
      ) {
        return "—";
      }

      return `${value} m/px`;
    };

  const formatSunAngle =
    (value) => {
      if (
        value === null ||
        value === undefined
      ) {
        return "—";
      }

      return `${Number(
        value
      ).toFixed(2)}°`;
    };

  const formatAcquisition =
    (dataset) => {
      if (
        !dataset.acquisition
          ?.datetime
      ) {
        return "—";
      }

      return dataset.acquisition.datetime.replace(
        "T",
        " "
      );
    };

  const sensorCount =
    new Set(
      datasets
        .map(
          (item) =>
            item.sensor
        )
        .filter(
          (sensor) =>
            sensor &&
            sensor !== "Unknown"
        )
    ).size;

  return (
    <div>
      <SectionTitle
        eyebrow="DATA CATALOG"
        title="Mission datasets"
        desc="Manage lunar imagery and metadata available to the LunaAlgin correspondence engine."
        action={
          <button
            className="primary-btn"
            onClick={
              loadDatasets
            }
            disabled={loading}
          >
            <Database size={17} />

            {loading
              ? "Refreshing..."
              : "Refresh catalog"}
          </button>
        }
      />

      <div className="stats-grid">
        <StatCard
          icon={Database}
          label="Total imagery"
          value={
            datasets.length
          }
          detail="files indexed"
        />

        <StatCard
          icon={FileImage}
          label="Available"
          value={
            datasets.filter(
              (item) =>
                item.status ===
                "Available"
            ).length
          }
          detail="ready for processing"
        />

        <StatCard
          icon={Layers3}
          label="Sensors"
          value={sensorCount}
          detail={
            sensorCount > 0
              ? "mission sensors detected"
              : "awaiting mission data"
          }
        />

        <StatCard
          icon={ShieldCheck}
          label="Catalog status"
          value={
            loading
              ? "..."
              : error
              ? "ERROR"
              : "ONLINE"
          }
          detail="backend connected"
        />
      </div>

      {error && (
        <div className="success-box">
          <X size={18} />

          <div>
            <b>
              Dataset error
            </b>

            <span>
              {error}
            </span>
          </div>
        </div>
      )}

      <div className="panel table-panel">
        <div className="card-head">
          <div>
            <span className="eyebrow">
              CATALOG
            </span>

            <h3>
              Indexed lunar imagery
            </h3>
          </div>

          <span className="count">
            {loading
              ? "Loading..."
              : `${datasets.length} indexed`}
          </span>
        </div>

        {loading ? (
          <div className="empty-state">
            <Activity size={28} />

            <h3>
              Loading datasets...
            </h3>

            <p>
              Reading indexed imagery from
              LunaAlgin backend.
            </p>
          </div>
        ) : datasets.length === 0 ? (
          <div className="empty-state">
            <Database size={32} />

            <h3>
              No datasets uploaded
            </h3>

            <p>
              Upload a lunar image from the
              Correspondence workspace to add it here.
            </p>

            <NavLink
              className="primary-btn"
              to="/correspondence"
            >
              <Upload size={17} />
              Upload image
            </NavLink>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>
                    Preview
                  </th>

                  <th>
                    Product
                  </th>

                  <th>
                    Sensor
                  </th>

                  <th>
                    Acquisition
                  </th>

                  <th>
                    Dimensions
                  </th>

                  <th>
                    Resolution
                  </th>

                  <th>
                    Sun angle
                  </th>

                  <th>
                    Size
                  </th>

                  <th>
                    Status
                  </th>
                </tr>
              </thead>

              <tbody>
                {datasets.map(
                  (dataset) => {
                    const sunAzimuth =
                      dataset
                        .illumination
                        ?.sun_azimuth_deg;

                    const sunElevation =
                      dataset
                        .illumination
                        ?.sun_elevation_deg;

                    return (
                      <tr
                        key={
                          dataset.filename
                        }
                      >
                        <td>
                          <img
                            src={`${BACKEND_URL}${dataset.input_url}`}
                            alt={
                              dataset.filename
                            }
                            style={{
                              width:
                                "72px",
                              height:
                                "48px",
                              objectFit:
                                "cover",
                              borderRadius:
                                "8px",
                              display:
                                "block",
                            }}
                          />
                        </td>

                        <td>
                          <div
                            style={{
                              display:
                                "flex",
                              flexDirection:
                                "column",
                              gap:
                                "3px",
                            }}
                          >
                            <b>
                              {
                                dataset.product_id
                              }
                            </b>

                            <small>
                              {
                                dataset.filename
                              }
                            </small>
                          </div>
                        </td>

                        <td>
                          <span className="status-badge">
                            {
                              dataset.sensor
                            }
                          </span>
                        </td>

                        <td>
                          {formatAcquisition(
                            dataset
                          )}
                        </td>

                        <td>
                          {
                            dataset
                              .spatial
                              ?.dimensions ||
                            "—"
                          }
                        </td>

                        <td>
                          {formatResolution(
                            dataset
                              .spatial
                              ?.resolution_m_per_pixel
                          )}
                        </td>

                        <td>
                          <div
                            style={{
                              display:
                                "flex",
                              flexDirection:
                                "column",
                              gap:
                                "3px",
                            }}
                          >
                            <span>
                              Az{" "}
                              {formatSunAngle(
                                sunAzimuth
                              )}
                            </span>

                            <small>
                              El{" "}
                              {formatSunAngle(
                                sunElevation
                              )}
                            </small>
                          </div>
                        </td>

                        <td>
                          {formatSize(
                            dataset
                              .file
                              ?.size_mb
                          )}
                        </td>

                        <td>
                          <span className="status-badge">
                            <span className="live-dot"></span>

                            {
                              dataset.status
                            }
                          </span>
                        </td>
                      </tr>
                    );
                  }
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="success-box">
        <ShieldCheck size={18} />

        <div>
          <b>
            Metadata pipeline ready
          </b>

          <span>
            Sensor, acquisition time,
            spatial resolution,
            illumination and
            geolocation fields are
            ready for official
            Chandrayaan-2 PDS metadata.
          </span>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   RESULTS
========================================================= */

function Results() {
  const [result, setResult] =
    useState(null);

  const loadResult = () => {
    const savedResult =
      localStorage.getItem(
        "lunaAlginResult"
      );

    if (savedResult) {
      try {
        setResult(
          JSON.parse(savedResult)
        );
      } catch (error) {
        console.error(
          "Failed to load result:",
          error
        );

        setResult(null);
      }
    } else {
      setResult(null);
    }
  };

  useEffect(() => {
    loadResult();

    const handleStorage =
      () => loadResult();

    window.addEventListener(
      "storage",
      handleStorage
    );

    return () =>
      window.removeEventListener(
        "storage",
        handleStorage
      );
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

            <h3>
              No correspondence result yet
            </h3>

            <p>
              Upload a reference and
              moving image, then run the
              LunaAlgin correspondence
              pipeline.
            </p>

            <NavLink
              className="primary-btn"
              to="/correspondence"
            >
              <Rocket size={17} />
              Start correspondence
            </NavLink>
          </div>
        </div>
      </div>
    );
  }

  const alignedImage =
    result.outputs?.aligned_image
      ? `${BACKEND_URL}${result.outputs.aligned_image}`
      : "";

  const correspondenceMap =
    result.outputs
      ?.correspondence_map
      ? `${BACKEND_URL}${result.outputs.correspondence_map}`
      : "";

  const differenceMap =
    result.outputs
      ?.difference_map
      ? `${BACKEND_URL}${result.outputs.difference_map}`
      : "";

  const inlierRatio =
    result.geometry
      ?.inlier_ratio ?? 0;

  const alignmentScore =
    result.registration
      ?.alignment_score ?? 0;

  const qualityMetrics =
    result.registration
      ?.quality_metrics || {};

  const reprojectionError =
    result.geometry
      ?.reprojection_error || {};

  const totalMatches =
    result.geometry
      ?.total_matches ?? 0;

  const inliers =
    result.geometry
      ?.inliers ?? 0;

  const outliers =
    result.geometry
      ?.outliers ?? 0;

  const transformationMatrix =
    getTransformationMatrix(
      result
    );

  const transformationModel =
    getTransformationModel(
      result
    );

  return (
    <div>
      <SectionTitle
        eyebrow="ANALYTICS"
        title="Correspondence results"
        desc="Inspect real match quality, geometric consistency and lunar image registration performance."
        action={
          <NavLink
            className="ghost-btn"
            to="/correspondence"
          >
            <GitCompare size={16} />
            New correspondence
          </NavLink>
        }
      />

      <div className="result-hero">
        <div>
          <span className="eyebrow">
            COMPLETED RUN
          </span>

          <h2>
            {result.input?.reference}

            <span>
              {" "}
              ↔{" "}
            </span>

            {result.input?.target}
          </h2>

          <p>
            Feature extraction ·
            Ratio-test matching ·
            RANSAC {transformationModel} ·
            Image registration
          </p>

          <small>
            Job ID: {result.job_id}
          </small>
        </div>

        <div className="score">
          {alignmentScore}%

          <small>
            alignment score
          </small>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={ScanSearch}
          label="Reference keypoints"
          value={
            result.features
              ?.reference_keypoints ?? 0
          }
          detail="detected"
        />

        <StatCard
          icon={ScanSearch}
          label="Moving keypoints"
          value={
            result.features
              ?.target_keypoints ?? 0
          }
          detail="detected"
        />

        <StatCard
          icon={GitCompare}
          label="Good matches"
          value={
            result.matching
              ?.good_matches ?? 0
          }
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
          <div className="image-card">
            <div className="image-card-header">
              <div>
                <span className="image-index">
                  01
                </span>

                <b>
                  Reference image
                </b>
              </div>

              <span className="image-type">
                FIXED
              </span>
            </div>

            <div className="real-image-preview">
              <img
                src={`${BACKEND_URL}/input/${encodeURIComponent(
                  result.input?.reference ||
                    ""
                )}`}
                alt="Reference lunar image"
              />
            </div>

            <small>
              Original coordinate system
            </small>
          </div>

          <div className="image-card">
            <div className="image-card-header">
              <div>
                <span className="image-index">
                  02
                </span>

                <b>
                  Moving image
                </b>
              </div>

              <span className="image-type">
                SOURCE
              </span>
            </div>

            <div className="real-image-preview">
              <img
                src={`${BACKEND_URL}/input/${encodeURIComponent(
                  result.input?.target ||
                    ""
                )}`}
                alt="Moving lunar image"
              />
            </div>

            <small>
              Input image before registration
            </small>
          </div>

          <div className="image-card">
            <div className="image-card-header">
              <div>
                <span className="image-index">
                  03
                </span>

                <b>
                  Aligned image
                </b>
              </div>

              <span className="image-type success">
                REGISTERED
              </span>
            </div>

            <div className="real-image-preview">
              {alignedImage ? (
                <img
                  src={alignedImage}
                  alt="Aligned lunar image"
                />
              ) : (
                <div className="empty-state">
                  <FileImage
                    size={24}
                  />

                  <span>
                    Aligned image unavailable
                  </span>
                </div>
              )}
            </div>

            <small>
              Moving image warped to reference coordinates
            </small>
          </div>
        </div>
      </div>

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
            {correspondenceMap ? (
              <img
                src={correspondenceMap}
                alt="LunaAlgin correspondence map"
              />
            ) : (
              <div className="empty-state">
                <CircleDot size={28} />

                <span>
                  Correspondence map unavailable
                </span>
              </div>
            )}
          </div>

          <div className="visual-summary">
            <span>
              <b>
                {totalMatches}
              </b>
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
            {differenceMap ? (
              <img
                src={differenceMap}
                alt="LunaAlgin difference map"
              />
            ) : (
              <div className="empty-state">
                <Activity size={28} />

                <span>
                  Difference map unavailable
                </span>
              </div>
            )}
          </div>

          <div className="visual-summary">
            <span>
              <b>
                {alignmentScore}%
              </b>
              alignment score
            </span>

            <span>
              <b>
                {inlierRatio}%
              </b>
              geometric confidence
            </span>
          </div>
        </div>
      </div>

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
              <span>
                Good matches
              </span>

              <b>
                {result.matching
                  ?.good_matches ?? 0}
              </b>
            </div>

            <small>
              ratio test
            </small>
          </div>

          <div className="metric-row">
            <div>
              <span>
                RANSAC inliers
              </span>

              <b>{inliers}</b>
            </div>

            <small>
              {inlierRatio}%
            </small>
          </div>

          <div className="metric-row">
            <div>
              <span>
                RANSAC outliers
              </span>

              <b>{outliers}</b>
            </div>

            <small>
              rejected
            </small>
          </div>

          <div className="metric-row">
            <div>
              <span>
                Average match distance
              </span>

              <b>
                {result.matching
                  ?.average_distance ?? 0}
              </b>
            </div>

            <small>
              descriptor distance
            </small>
          </div>

          <div className="metric-row">
            <div>
              <span>
                Best match distance
              </span>

              <b>
                {result.matching
                  ?.best_distance ?? 0}
              </b>
            </div>

            <small>
              strongest match
            </small>
          </div>
        </div>

        <div className="panel">
          <div className="card-head">
            <div>
              <span className="eyebrow">
                GEOMETRIC MODEL
              </span>

              <h3>
                {transformationModel} matrix
              </h3>
            </div>

            <Boxes size={19} />
          </div>

          <div className="matrix-box">
            {transformationMatrix.length >
            0 ? (
              transformationMatrix.map(
                (row, rowIndex) => (
                  <div
                    className="matrix-row"
                    key={rowIndex}
                  >
                    {row.map(
                      (
                        value,
                        colIndex
                      ) => (
                        <code
                          key={
                            colIndex
                          }
                        >
                          {formatNumber(
                            value,
                            6
                          )}
                        </code>
                      )
                    )}
                  </div>
                )
              )
            ) : (
              <div className="empty-state">
                <Boxes size={24} />

                <span>
                  Transformation matrix unavailable
                </span>
              </div>
            )}
          </div>

          <div className="matrix-info">
            <span>
              <b>Model</b>
              {transformationModel}
            </span>

            <span>
              <b>
                RANSAC threshold
              </b>
              {result.parameters
                ?.reprojection_threshold ??
                result.reprojection_threshold ??
                5}{" "}
              px
            </span>

            <span>
              <b>
                Inlier ratio
              </b>
              {inlierRatio}%
            </span>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="card-head">
          <div>
            <span className="eyebrow">
              SCIENTIFIC VALIDATION
            </span>

            <h3>
              Registration quality metrics
            </h3>
          </div>

          <Gauge size={19} />
        </div>

        <div className="stats-grid">
          <StatCard
            icon={Gauge}
            label="RMSE"
            value={
              qualityMetrics.rmse ??
              0
            }
            detail="lower is better"
          />

          <StatCard
            icon={ShieldCheck}
            label="SSIM"
            value={
              qualityMetrics.ssim ??
              0
            }
            detail="structural similarity"
          />

          <StatCard
            icon={GitCompare}
            label="NCC"
            value={
              qualityMetrics.ncc ??
              0
            }
            detail="correlation coefficient"
          />

          <StatCard
            icon={ScanSearch}
            label="Mean reprojection"
            value={`${reprojectionError.mean_error ?? 0} px`}
            detail="geometric error"
          />
        </div>

        <div className="metric-row">
          <div>
            <span>
              Median reprojection error
            </span>

            <b>
              {reprojectionError
                .median_error ??
                0}{" "}
              px
            </b>
          </div>

          <small>
            RANSAC inliers
          </small>
        </div>

        <div className="metric-row">
          <div>
            <span>
              Maximum reprojection error
            </span>

            <b>
              {reprojectionError
                .max_error ??
                0}{" "}
              px
            </b>
          </div>

          <small>
            worst inlier
          </small>
        </div>

        <div className="metric-row">
          <div>
            <span>
              Minimum reprojection error
            </span>

            <b>
              {reprojectionError
                .min_error ??
                0}{" "}
              px
            </b>
          </div>

          <small>
            best inlier
          </small>
        </div>
      </div>

      <div className="panel run-summary">
        <div>
          <span className="eyebrow">
            PIPELINE STATUS
          </span>

          <h3>
            Registration completed successfully
          </h3>

          <p>
            {inliers} of{" "}
            {totalMatches} matched
            feature pairs survived
            geometric verification.
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

/* =========================================================
   SETTINGS
========================================================= */

function Settings() {
  return (
    <div>
      <SectionTitle
        eyebrow="SYSTEM"
        title="Engine settings"
        desc="Configure defaults used by the LUNA processing workflow."
      />

      <div className="panel settings-panel">
        {[
          [
            "Default detector",
            "SIFT / SuperPoint hybrid",
            "Feature extraction",
          ],
          [
            "Matcher",
            "FLANN + ratio test",
            "Descriptor matching",
          ],
          [
            "RANSAC threshold",
            "3.0 px",
            "Geometric verification",
          ],
          [
            "Output format",
            "PNG + JSON",
            "Artifacts",
          ],
          [
            "API endpoint",
            "http://localhost:8000",
            "Backend service",
          ],
        ].map(
          ([a, b, c]) => (
            <div
              className="setting-row"
              key={a}
            >
              <div>
                <b>{a}</b>

                <small>{c}</small>
              </div>

              <code>{b}</code>
            </div>
          )
        )}
      </div>
    </div>
  );
}

/* =========================================================
   APP
========================================================= */

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route
          path="/"
          element={<Overview />}
        />

        <Route
          path="/correspondence"
          element={
            <Correspondence />
          }
        />

        <Route
          path="/datasets"
          element={<Datasets />}
        />

        <Route
          path="/results"
          element={<Results />}
        />

        <Route
          path="/settings"
          element={<Settings />}
        />
      </Routes>
    </Layout>
  );
}