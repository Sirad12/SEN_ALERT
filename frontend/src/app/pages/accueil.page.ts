import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CarteComponent } from '../ui/carte.component';
import { DetailComponent } from '../ui/detail.component';
import { COULEURS, communeDe, SignalementService, STATUTS, TYPES } from '../signalement.service';

@Component({
  selector: 'app-accueil',
  imports: [FormsModule, RouterLink, CarteComponent, DetailComponent],
  template: `
    <section class="hero"><div class="hero-in">
      <h1>Un caniveau bouché ? Signalez-le avant la saison des pluies.</h1>
      <p>Photographiez le problème, placez-le sur la carte et recevez un code pour suivre son traitement. Aucun compte à créer.</p>
      <a routerLink="/signaler" class="btn clair">Signaler un problème</a>
      <a routerLink="/suivre" class="btn contour">Suivre un signalement</a>
    </div></section>

    <div class="tuiles">
      <a class="tuile" routerLink="/signaler"><b>Signaler</b><span>Type de problème, photo et position sur la carte.</span></a>
      <a class="tuile" routerLink="/suivre"><b>Suivre</b><span>Retrouvez l’état de votre signalement avec son code.</span></a>
      <button class="tuile" (click)="versCarte()"><b>Consulter la carte</b><span>Tous les points signalés dans les communes.</span></button>
    </div>

    <div class="chiffres">
      @for (c of chiffres(); track c.l) { <div><b>{{ c.n }}</b><span>{{ c.l }}</span></div> }
    </div>

    <div class="page" id="carte">
      <div class="entete-page">
        <div><h1>Carte des signalements</h1>
          <p class="mut">Cliquez sur un point pour voir sa photo, son statut et son historique.</p></div>
      </div>
      <div class="split">
        <section>
          <div class="duo">
            <select aria-label="Filtrer par type" [ngModel]="type()" (ngModelChange)="type.set($event)">
              <option value="">Tous les types</option>
              @for (t of types; track t) { <option>{{ t }}</option> }
            </select>
            <select aria-label="Filtrer par statut" [ngModel]="statut()" (ngModelChange)="statut.set($event)">
              <option value="">Tous les statuts</option>
              @for (s of statuts; track s) { <option>{{ s }}</option> }
            </select>
          </div>
          <app-carte [signalements]="visibles()" [selection]="choix()" (choisirSignalement)="choix.set($event)"/>
          <p class="mut">
            @for (s of statuts; track s) { <span class="st" [style.--c]="couleurs[s]" style="margin-right:16px">{{ s }}</span> }
          </p>
        </section>
        <aside><app-detail [s]="courant()"/></aside>
      </div>
    </div>`,
})
export class AccueilPage {
  svc = inject(SignalementService);
  types = TYPES; statuts = STATUTS; couleurs = COULEURS; commune = communeDe;
  type = signal(''); statut = signal(''); choix = signal<string | null>(null);
  visibles = computed(() => this.svc.liste().filter(r =>
    (!this.type() || r.type === this.type()) && (!this.statut() || r.statut === this.statut())));
  courant = computed(() => this.svc.liste().find(r => r.id === this.choix()));
  chiffres = computed(() => {
    const l = this.svc.liste();
    return [
      { n: l.length, l: 'signalements enregistrés' },
      { n: new Set(l.map(r => communeDe(r.x, r.y))).size, l: 'communes concernées' },
      { n: l.filter(r => r.statut === 'En traitement').length, l: 'en traitement' },
      { n: l.filter(r => r.statut === 'Résolu').length, l: 'résolus' },
    ];
  });
  versCarte() { document.getElementById('carte')?.scrollIntoView({ behavior: 'smooth' }); }
}
