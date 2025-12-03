# Kerhotila

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään sovellukseen ajanvarauksia. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään ajanvarauksia.
* Käyttäjä näkee sovellukseen lisätyt ajanvaraukset. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät ajanvaraukset.
* Käyttäjä pystyy etsimään ajanvarauksia hakusanalla tai muulla perusteella. Käyttäjä pystyy hakemaan sekä itse lisäämiään että muiden käyttäjien lisäämiä ajanvarauksia.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät ajanvaraukset.
* Käyttäjä pystyy valitsemaan ajanvaraukselle yhden tai useamman luokittelun (esim. tilaisuuden luokittelu, osallistujamäärä ja tilaisuuden avoimuus).
* Sovelluksessa voi myös ilmoittautua ajanvarauksiin. Käyttäjä pystyy ilmoittautumaan omiin ja muiden käyttäjien ajanvarauksiin.

## Sovelluksen asennus

Asenna 'flask'-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut:

```
$ sqlite3 database.db < schema.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```