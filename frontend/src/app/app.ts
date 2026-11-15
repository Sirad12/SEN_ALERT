import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="entete">
      <div class="entete-in">
        <a class="marque" routerLink="/">
          <img src="logo.svg" alt="" width="42" height="42" style="margin:0">
          <span><b>SenAlert</b><small>Signalement des points bloqués</small></span>
        </a>
        @if (admin()) {
          <span class="mut">Espace réservé</span>
        } @else {
          <nav>
            @for (l of liens; track l[0]) {
              <a [routerLink]="l[0]" routerLinkActive="actif" [routerLinkActiveOptions]="{ exact: true }">{{ l[1] }}</a>
            }
          </nav>
        }
      </div>
    </header>
    <router-outlet />
    <footer class="pied">
      <div class="pied-in">
        <div><h3>SenAlert</h3>
          <p>Chaque habitant peut signaler une rue, un canal ou un caniveau bouché, pour que les communes agissent avant les pluies.</p></div>
        <div><h3>Services</h3>
          <a routerLink="/signaler">Signaler un problème</a>
          <a routerLink="/suivre">Suivre un signalement</a>
          <a routerLink="/">Carte des signalements</a></div>
      </div>
      <div class="copy">© 2026 SenAlert · Données fictives</div>
    </footer>`,
})
export class App {
  private router = inject(Router);
  liens = [['/', 'Accueil'], ['/signaler', 'Signaler'], ['/suivre', 'Suivre un signalement']];
  private url = toSignal(
    this.router.events.pipe(filter(e => e instanceof NavigationEnd), map(() => this.router.url)),
    { initialValue: this.router.url });
  admin = computed(() => this.url().startsWith('/admin'));
}
