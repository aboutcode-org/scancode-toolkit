/*
 * Copyright (C) 1997 Rodolfo Borges <barrett@labma.ufrj.br>
 * Copyright (C) 1998-2009 Stephan Kulow <coolo@kde.org>
 * Copyright (C) 2010 Parker Coates <coates@kde.org>
 *
 * License of original code:
 * -------------------------------------------------------------------------
 *   Permission to use, copy, modify, and distribute this software and its
 *   documentation for any purpose and without fee is hereby granted,
 *   provided that the above copyright notice appear in all copies and that
 *   both that copyright notice and this permission notice appear in
 *   supporting documentation.
 *
 *   This file is provided AS IS with no warranties of any kind.  The author
 *   shall have no liability with respect to the infringement of copyrights,
 *   trade secrets or any patents by this file or any part thereof.  In no
 *   event will the author be liable for any lost revenue or profits or
 *   other special, indirect and consequential damages.
 * -------------------------------------------------------------------------
 *
 * License of modifications/additions made after 2009-01-01:
 * -------------------------------------------------------------------------
 *   This program is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU General Public License as
 *   published by the Free Software Foundation; either version 2 of 
 *   the License, or (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * -------------------------------------------------------------------------
 */

#include "mod3.h"

#include "dealerinfo.h"
#include "patsolve/mod3solver.h"

#include <KLocalizedString>


Mod3::Mod3( const DealerInfo * di )
  : DealerScene( di )
{
}


void Mod3::initialize()
{
    // Piles are placed very close together. Set layoutSpacing to 0 to prevent
    // interference between them.
    setLayoutSpacing(0.0);

    const qreal dist_x = 1.114;
    const qreal dist_y = 1.31;
    const qreal bottomRowY = 3 * dist_y + 0.2;
    const qreal rightColumX = 8 * dist_x + 0.8;

    // This patience uses 2 deck of cards.
    setDeckContents( 2 );

    talon = new PatPile( this, 0, QStringLiteral("talon") );
    talon->setPileRole(PatPile::Stock);
    talon->setLayoutPos(rightColumX, bottomRowY);
    talon->setSpread(0, 0);
    talon->setKeyboardSelectHint( KCardPile::NeverFocus );
    talon->setKeyboardDropHint( KCardPile::NeverFocus );
    connect( talon, &KCardPile::clicked, this, &DealerScene::drawDealRowOrRedeal );

    aces = new PatPile( this, 50, QStringLiteral("aces"));
    aces->setPileRole(PatPile::FoundationType1);
    aces->setLayoutPos(rightColumX, 0.5);
    aces->setBottomPadding( 2.5 );
    aces->setKeyboardSelectHint( KCardPile::NeverFocus );
    aces->setKeyboardDropHint( KCardPile::ForceFocusTop );

    for ( int r = 0; r < 4; ++r )
    {
        for ( int c = 0; c < 8; ++c )
        {
            int pileIndex = r * 10 + c  + 1;
            QString objectName = QStringLiteral( "stack%1_%2" ).arg( r ).arg( c );
            stack[r][c] = new PatPile( this, pileIndex, objectName );

            // The first 3 rows are the playing field, the fourth is the store.
            if ( r < 3 )
            {
                stack[r][c]->setLayoutPos( dist_x * c, dist_y * r );
                // Very tight spread makes it easy to quickly tell number of
                // cards in each pile and we don't care about the cards beneath.
                stack[r][c]->setSpread( 0, 0.08 );
                stack[r][c]->setBottomPadding( 0.23 );
            }
            else
            {
                stack[r][c]->setLayoutPos( dist_x * c, bottomRowY );
                stack[r][c]->setBottomPadding( 0.8 );
            }
            stack[r][c]->setPileRole( r == 0 ? PatPile::FoundationType2
                                      : r == 1 ? PatPile::FoundationType3
                                      : r == 2 ? PatPile::FoundationType4
                                      : PatPile::Tableau );
            stack[r][c]->setHeightPolicy( KCardPile::GrowDown );
            stack[r][c]->setKeyboardSelectHint( KCardPile::AutoFocusTop );
            stack[r][c]->setKeyboardDropHint( KCardPile::AutoFocusTop );
        }
    }

    setActions(DealerScene::Hint | DealerScene::Demo  | DealerScene::Deal);
    setSolver( new Mod3Solver( this ) );
}

bool mod3CheckAdd(int baseRank, const QList<KCard*> & oldCards, const QList<KCard*> & newCards)
{
    if (oldCards.isEmpty())
        return newCards.first()->rank() == baseRank;
    else
        return oldCards.first()->rank() == baseRank
               && newCards.first()->suit() == oldCards.last()->suit()
               && newCards.first()->rank() == oldCards.last()->rank() + 3;
}

bool Mod3::checkAdd(const PatPile * pile, const QList<KCard*> & oldCards, const QList<KCard*> & newCards) const
{
    switch (pile->pileRole())
    {
    case PatPile::FoundationType1:
        return newCards.size() == 1 && newCards.first()->rank() == KCardDeck::Ace;
    case PatPile::FoundationType2:
        return mod3CheckAdd(KCardDeck::Two, oldCards, newCards);
    case PatPile::FoundationType3:
        return mod3CheckAdd(KCardDeck::Three, oldCards, newCards);
    case PatPile::FoundationType4:
        return mod3CheckAdd(KCardDeck::Four, oldCards, newCards);
    case PatPile::Tableau:
        return oldCards.isEmpty();
    case PatPile::Stock:
    default:
        return false;
    }
}

bool Mod3::checkRemove(const PatPile * pile, const QList<KCard*> & cards) const
{
    switch (pile->pileRole())
    {
    case PatPile::FoundationType2:
    case PatPile::FoundationType3:
    case PatPile::FoundationType4:
    case PatPile::Tableau:
        return cards.first() == pile->topCard();
    case PatPile::FoundationType1:
    case PatPile::Stock:
    default:
        return false;
    }
}


void Mod3::cardsMoved( const QList<KCard*> & cards, KCardPile * oldPile, KCardPile * newPile )
{
    if ( oldPile->isEmpty() && !talon->isEmpty() )
    {
        PatPile * p = dynamic_cast<PatPile*>( oldPile );
        if ( p && p->pileRole() == PatPile::Tableau )
            flipCardToPile( talon->topCard(), oldPile, DURATION_MOVE );
    }

    DealerScene::cardsMoved( cards, oldPile, newPile );
}


void Mod3::restart( const QList<KCard*> & cards )
{
    foreach ( KCard * c, cards )
    {
        c->setPos( talon->pos() );
        c->setFaceUp( false );
        talon->add( c );
    }

    for ( int r = 0; r < 4; r++ )
    {
        for ( int c = 0; c < 8; ++c )
        {
            KCard * card = talon->topCard();
            card->setFaceUp( true );
//             moveCardToPileAtSpeed( card, stack[r][c], DEAL_SPEED );

            addCardForDeal( stack[r][c], card, true, talon->pos() );

            // Fudge the z values to keep cards from popping through one another.
            card->setZValue( card->zValue() + ((4 - r) * (4 - r)) + ((8 - c) * (8 - c)) );
        }
    }

    startDealAnimation();
    emit newCardsPossible(true);
}


bool Mod3::newCards()
{
    if ( talon->isEmpty() )
        return false;

    for ( int c = 0; c < 8; ++c )
    {
        if ( talon->isEmpty() )
            break;

        flipCardToPileAtSpeed( talon->topCard(), stack[3][c], DEAL_SPEED * 2 );
    }

    if (talon->isEmpty())
        emit newCardsPossible(false);

    return true;
}


void Mod3::setGameState( const QString & state )
{
    Q_UNUSED( state );
    emit newCardsPossible(!talon->isEmpty());
}



static class Mod3DealerInfo : public DealerInfo
{
public:
    Mod3DealerInfo()
      : DealerInfo(I18N_NOOP("Mod3"), Mod3Id)
    {}

    DealerScene *createGame() const Q_DECL_OVERRIDE
    {
        return new Mod3( this );
    }
} mod3DealerInfo;



