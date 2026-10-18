import { AppBar, Box, Button, Container, CssBaseline, Toolbar, Typography } from '@mui/material'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { BrowserRouter, Link as RouterLink, Route, Routes } from 'react-router-dom'
import { PageViewLogger } from './components/PageViewLogger'
import { ArticlePage } from './pages/ArticlePage'
import { LoginPage } from './pages/LoginPage'
import { SignupPage } from './pages/SignupPage'
import './index.css'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#285b52' },
    background: { default: '#f4f4f1', paper: '#ffffff' },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
    h1: { fontSize: 'clamp(2.4rem, 5vw, 4.6rem)', fontWeight: 700, lineHeight: 1.04 },
    h2: { fontSize: '1.65rem', fontWeight: 700, lineHeight: 1.2 },
  },
  shape: { borderRadius: 16 },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <PageViewLogger />
        <AppBar position="static" color="inherit" elevation={0}>
          <Toolbar className="site-toolbar">
            <Box component={RouterLink} to="/" className="brand">
              <span className="brand-mark" aria-hidden="true" />
              <Typography variant="h6" component="span">
                Signal &amp; Circuit
              </Typography>
            </Box>
            <Box className="site-nav">
              <Button component={RouterLink} to="/" className="nav-link">
                Article
              </Button>
              <Button component={RouterLink} to="/signup" className="nav-link">
                Signup
              </Button>
              <Button component={RouterLink} to="/login" className="nav-link">
                Login
              </Button>
            </Box>
          </Toolbar>
        </AppBar>
        <Container component="main" maxWidth="md" className="page-content">
          <Routes>
            <Route path="/" element={<ArticlePage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="*"
              element={
                <Typography variant="h1" component="h1">
                  Page not found
                </Typography>
              }
            />
          </Routes>
        </Container>
        <Box component="footer" className="site-footer">
          Local research benchmark · synthetic data only
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
