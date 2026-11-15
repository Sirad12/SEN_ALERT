import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';

describe('App', () => {
  it('affiche la navigation publique sans lien vers l’administration', async () => {
    await TestBed.configureTestingModule({ imports: [App], providers: [provideRouter([])] }).compileComponents();
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const el = fixture.nativeElement as HTMLElement;
    const texte = el.textContent ?? '';
    expect(texte).toContain('Signaler');
    expect(texte).toContain('Suivre un signalement');
    expect(texte).toContain('Accueil');
    expect(texte.toLowerCase()).not.toContain('administrat');
    expect(el.querySelector('a[href="/admin"]')).toBeNull();
  });
});
