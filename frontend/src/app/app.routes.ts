import { Routes } from '@angular/router';
import { AccueilPage } from './pages/accueil.page';
import { SignalerPage } from './pages/signaler.page';
import { SuivrePage } from './pages/suivre.page';
import { AdminPage } from './pages/admin.page';

export const routes: Routes = [
  { path: '', component: AccueilPage, title: 'SenAlert · Carte des signalements' },
  { path: 'signaler', component: SignalerPage, title: 'SenAlert · Signaler un problème' },
  { path: 'suivre', component: SuivrePage, title: 'SenAlert · Suivre un signalement' },
  // Aucun lien public vers cette page : on y accède uniquement en tapant /admin.
  { path: 'admin', component: AdminPage, title: 'Espace administrateur' },
  { path: '**', redirectTo: '' },
];
