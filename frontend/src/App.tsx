import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import DCFScreen from './pages/DCFScreen';
import IngestionScreen from './pages/IngestionScreen';
import AssumptionsScreen from './pages/AssumptionsScreen';
import ModelScreen from './pages/ModelScreen';
import CompsScreen from './pages/CompsScreen';
import SensitivityScreen from './pages/SensitivityScreen';
import AuditScreen from './pages/AuditScreen';
import ExportScreen from './pages/ExportScreen';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dcf" element={<DCFScreen />} />
          <Route path="/ingest" element={<IngestionScreen />} />
          <Route path="/assumptions" element={<AssumptionsScreen />} />
          <Route path="/model" element={<ModelScreen />} />
          <Route path="/comps" element={<CompsScreen />} />
          <Route path="/sensitivity" element={<SensitivityScreen />} />
          <Route path="/audit" element={<AuditScreen />} />
          <Route path="/export" element={<ExportScreen />} />
          {/* Fallback route */}
          <Route path="*" element={<div className="p-8 text-txt-muted">Page Under Construction</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
