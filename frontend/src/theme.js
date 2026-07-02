import { createTheme } from '@mui/material/styles';

// HelpRoute palette (from the prototype spec).
export const COLORS = {
  sidebarBg: '#0B2B36',
  sidebarActive: '#17A589',
  primary: '#0F6E5C',
  primaryHover: '#0C5849',
  pageBg: '#F4F8F7',
  cardBorder: '#DCE7E4',
  warning: '#C8821F',
  danger: '#B6432F',
};

const headingFont = '"Space Grotesk", "Segoe UI", sans-serif';

const theme = createTheme({
  palette: {
    primary: { main: COLORS.primary, dark: COLORS.primaryHover },
    secondary: { main: COLORS.sidebarBg },
    success: { main: COLORS.primary },
    warning: { main: COLORS.warning },
    error: { main: COLORS.danger },
    background: { default: COLORS.pageBg },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Inter", "Segoe UI", Arial, sans-serif',
    h4: { fontFamily: headingFont, fontWeight: 700 },
    h5: { fontFamily: headingFont, fontWeight: 700 },
    h6: { fontFamily: headingFont, fontWeight: 700 },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true }, styleOverrides: { root: { textTransform: 'none', fontWeight: 600 } } },
    MuiPaper: { styleOverrides: { root: { backgroundImage: 'none', border: `1px solid ${COLORS.cardBorder}` } } },
    MuiCard: { styleOverrides: { root: { border: `1px solid ${COLORS.cardBorder}` } } },
  },
});

export default theme;
