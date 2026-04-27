import { COLORS, TOKENS } from "../../Constants";

const DocumentBadge = ({ type, count, icon, scale = 1 }) => {
  const typeConfig = {
    signed: {
      bg: COLORS.signedContracts,
      label: "Signed Contracts",
      icon: "📜",
    },
    pending: {
      bg: COLORS.pendingSignature,
      label: "Pending Signature",
      icon: "📋",
    },
    draft: { bg: COLORS.drafts, label: "Drafts", icon: "📄" },
    expired: { bg: COLORS.expired, label: "Critical (≤ 7 days)", icon: "⚠️" },
    expiringSoon: {
      bg: COLORS.expiringSoon,
      label: "Warning (≤ 30 days)",
      icon: "⚡",
    },
    notice: { bg: COLORS.notices, label: "Notices (≤ 60 days)", icon: "📢" },
  };

  const config = typeConfig[type] || typeConfig.signed;
  const width = Math.round(342 * scale);
  const height = Math.round(85 * scale);
  const padding = Math.round(12 * scale);
  const borderRadius = Math.round(22 * scale);

  return (
    <div
      style={{
        width: `${width}px`,
        height: `${height}px`,
        padding: `${padding}px`,
        background: config.bg,
        boxShadow: TOKENS.shadow.sm,
        borderRadius: `${borderRadius}px`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        flexShrink: 0,
      }}
    >
      <div
        style={{
          fontSize: `${Math.round(20 * scale)}px`,
          fontWeight: 500,
          color: COLORS.darkText,
          fontFamily: "Poppins, sans-serif",
          lineHeight: `${Math.round(30 * scale)}px`,
        }}
      >
        {config.label}
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontSize: `${Math.round(20 * scale)}px`,
            fontWeight: 500,
            color: COLORS.darkText,
            fontFamily: "Poppins, sans-serif",
            lineHeight: `${Math.round(30 * scale)}px`,
          }}
        >
          {count}
        </div>
        <div style={{ fontSize: `${Math.round(24 * scale)}px` }}>
          {icon || config.icon}
        </div>
      </div>
    </div>
  );
};

export default DocumentBadge;
