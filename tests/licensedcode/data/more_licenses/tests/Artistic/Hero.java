/*
 * Hero.java
 * Copyright (C) 2001, Sandra and Klaus Rennecke.
 *
 * This software may be copied only under the terms of the
 * Artistic License, which can be found in the project documentation
 * and at http://www.opensource.org/licenses/artistic-license.html.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
 * MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 *
 * $Date: 2004/04/18 07:00:58 $
 */

package saga.model;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import saga.control.Control;
import saga.control.HeroLocation;
import saga.model.features.Guild;
import saga.model.features.Shop;
import saga.model.items.Armor;
import saga.model.items.GoldCoin;
import saga.model.items.Weapon;



/**
 * TODO: documentation
 * @author  Sandra Rennecke
 * @version $Revision: 1.1 $
 */
public class Hero extends Mob implements Serializable {
    
    public static final String PROPERTY_HP = "Hero.hp";
    public static final String PROPERTY_GOLD = "Hero.gold";
    public static final String PROPERTY_WC = "Hero.wc";
    public static final String PROPERTY_AC = "Hero.ac";
    public static final String PROPERTY_AP = "Hero.ap";
    public static final String PROPERTY_ATTACK = "Hero.attack";
    public static final String PROPERTY_SKILL = "Hero.skill";
    
    
    private HashMap skills;
    Inventory i;
    private boolean male = false;
    
    private Weapon weapon;
    private ArmorSlots wornArmor;
    protected long creationDate;
    protected long birthDate;
    protected int skillPoints;
    
    private static final long serialVersionUID = 4731606345656457822L;
    
    
    
    /** Deserialization constructor. */
    protected Hero() {
    }
    
    public Hero(String name) {
        this(name, 1, 2, 1, 1, 1, 1, 1);
    }
    
    public Hero(String name, int str, int con, int aur,
                int wis, int dex, int agi, int cha) {
        
        super(name, dex, str, con * 10, 1);
        
        skills = new HashMap();
        i = new Inventory(str * 10);
        
        this.str = str;
        this.con = con;
        this.aur = aur;
        this.wis = wis;
        this.dex = dex;
        this.agi = agi;
        this.cha = cha;
        
        weapon = null;
        wornArmor = new ArmorSlots();
        creationDate = Time.getTime().getRealTime();
        skillPoints = 0;
        
        // establish listener
        readResolve();
    }
    
    /** Resolve this hero instance after deserialization. This
     * re-establishes listener relations. */
    private Object readResolve() {
        if (i != null) {
            // add a property change listener to inventory to forward
            // action point change
            i.addPropertyChangeListener(new PropertyChangeListener() {
                public void propertyChange(PropertyChangeEvent ev) {
                    if (propertyChangeSupport != null) {
                        propertyChangeSupport.firePropertyChange
                        (PROPERTY_AP, -1, getActionPoints());
                    }
                }
            });
        }
        return this;
    }
    
    public void addSkillPoints(int n) {
        skillPoints += n;
    }
    public int getSkillPoints() {
        return skillPoints;
    }
    
    public void addSkill(String name, double value, boolean silent) {
        
        if (!skills.containsKey(name)) {
            Integer newValue = new Integer((int)(value * 10));
            skills.put(name, newValue);
            if (propertyChangeSupport != null) {
                propertyChangeSupport.firePropertyChange
                (PROPERTY_SKILL, name, newValue);
            }
            if (!silent) {
                Control.message(getName() + " learned " + name
                                + "(" + value + ")");
            }
            return;
        }
        int oldval = ((Integer)skills.get(name)).intValue();
        skills.remove(name);
        int val = oldval+((int)(value * 10));
        Integer newValue = new Integer(val);
        skills.put(name, newValue);
        if (propertyChangeSupport != null) {
            propertyChangeSupport.firePropertyChange
            (PROPERTY_SKILL, name, newValue);
        }
        if (!silent) {
            Control.message(getName() + " gained " + name
                            + "(" + ((double)(val / 10.0)) + ")");
        }
        if (name.equals(Skill.ATTACK)) {
            if (propertyChangeSupport != null) {
                propertyChangeSupport.firePropertyChange
                (PROPERTY_ATTACK, oldval / 10, getAttack());
            }
        }
    }
    public void addSkill(String name, double value) {
        addSkill(name, value, false);
    }
    
    public double skillValue(String name) {
        if (!skills.containsKey(name)) {
            return 0.0;
        }
        return (((Integer)skills.get(name)).intValue() / 10.0);
    }
    
    public Set getSkills() {
        return skills.entrySet();
    }
    public Inventory getInventory() {
        return i;
    }
    
    public void setMale(boolean val) {
        male = val;
    }
    
    public boolean isMale() {
        return male;
    }
    public boolean isFemale() {
        return !male;
    }
    
    public int getStr() {
        return str;
    }
    public void setStr(int newVal) {
        int oldWc = getWc();
        int oldAp = getActionPoints();
        str = newVal;
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_WC, oldWc, getWc());
            propertyChangeSupport
                .firePropertyChange(PROPERTY_AP, oldAp, getActionPoints());
        }
        
    }
    public int getCon(){
        return con;
    }
    
    public void setCon(int newVal) {
        con = newVal;
        maxhp = con * 10;
        setHp(con * 10);
    }
    
    public int getAur() {
        return aur;
    }
    public int getWis() {
        return wis;
    }
    public int getDex() {
        return dex;
    }
    public void setDex(int newVal) {
        int oldAc = getAc();
        dex = newVal;
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_AC, oldAc, getAc());
        }
    }
    
    public int getAgi() {
        return agi;
    }
    
    public void setAgi(int newVal) {
        int oldAc = getAc();
        agi = newVal;
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_AC, oldAc, getAc());
        }
    }
    
    public int getCha(){
        return cha;
    }
    public int getGold(){
        return i.getNumber(Shop.coin);
    }
    
    /**
     * Wield the given weapon <var>w</var>.
     * Previously wielded weapon is removed and added to the inventory.
     * @param w The weapon to wield.
     * @param silent True to suppress output.
     */
    public void wield(Weapon w, boolean silent) {
        if (w != null && !w.canWield(this)) {
            if (!silent) {
                Control.infoIcon("You are not allowed to wield " + w,
                                 "Wielding Weapon", w);
            }
            return;
        }
        
        int oldWc = getWc();
        
        Weapon oldWeapon = weapon;
        if (oldWeapon != null) {
            if (!silent) {
                Control.infoIcon("You unwield " + oldWeapon,
                                 "Wielding Weapon", oldWeapon);
            }
            weapon = null;
            addItem(oldWeapon, 1, silent);
        }
        
        if (w != null) {
            removeItem(w, 1, silent);
            weapon = w;
            if(!silent) {
                Control.infoIcon("You wield " + w, "Wielding Weapon", w);
            }
        }
        
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_WC, oldWc, getWc());
        }
    }
    
    /**
     * Wield the given weapon <var>w</var>.
     * Previously wielded weapon is removed and added to the inventory.
     * @param w The weapon to wield.
     */
    public void wield(Weapon w) {
        wield(w, false);
    }
    
    /**
     * Wear the given armor <var>a</var>, in the appropriate slot.
     * Previously worn armor is removed and added to the inventory.
     * @param a The armor to wear.
     * @param silent True to suppress output.
     */
    public void wear(Armor a, boolean silent) {
        int oldAc = getAc();
        
        if (a == null) {
            Control.error("Hero.wear(null)");
            return;
        }
        Armor oldArmor = wornArmor.getArmor(a.getSlot());
        if (oldArmor!=null) {
            addItem(oldArmor, 1, silent);
        }
        wornArmor.wear(a);
        removeItem(a, 1, silent);
        
        if (!silent) {
            Control.infoIcon("You wear " + a, "Wearing Armor", a);
        }
        
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_AC, oldAc, getAc());
        }
    }
    
    /**
     * Wear the given armor <var>a</var>, in the appropriate slot.
     * Previously worn armor is removed and added to the inventory.
     * @param a The armor to wear.
     */
    public void wear(Armor a) {
        wear(a, false);
    }
    
    /**
     * Remove the worn armor <var>a</var>.
     * @param a The armor to remove.
     * @param silent True to suppress output.
     */
    public void removeArmor(Armor a, boolean silent) {
        int oldAc = getAc();
        
        if (a == null) {
            Control.error("Hero.removeArmor(null)");
            return;
        }
        
        if (!wornArmor.remove(a)) {
            Control.error("Cannot remove armor "+a);
            return;
        }
        addItem(a, 1, silent);
                
        if (!silent) {
            Control.infoIcon("You stop wearing " + a, "Wearing Armor", a);
        }
        
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_AC, oldAc, getAc());
        }
    }
    
    public Object[] getAllWeapons() {
        ArrayList l = new ArrayList();
        Iterator it = i.getMiscItems().iterator();
        while (it.hasNext()) {
            Object o = it.next();
            if (o instanceof Weapon) {
                l.add(o);
            }
        }
        return l.toArray();
    }
    
    public Object[] getAllArmor() {
        ArrayList l = new ArrayList();
        Iterator it = i.getMiscItems().iterator();
        while (it.hasNext()) {
            Object o = it.next();
            if (o instanceof Armor) {
                l.add(o);
            }
        }
        return l.toArray();
    }
    
    public Weapon getWeapon() {
        return weapon;
    }
    
    /**
     * Get the worn armor in <var>slot</var>, if any.
     * @param slot The slot to query for armor.
     * @return the armor worn in <var>slot</var>, or null.
     */
    public Armor getArmor(int slot) {
        return wornArmor == null ? null : wornArmor.getArmor(slot);
    }
    
    /**
     * Add <var>number</var> <var>item</var>s to inventory.
     * @return true on success, false otherwise.
     * @param item The item to add.
     * @param number The amount of items to add.
     */
    public boolean addItem(Item item, int number) {
        return addItem(item, number, false);
    }
    
    /**
     * Add <var>number</var> <var>item</var>s to inventory.
     * @return true on success, false otherwise.
     * @param silent True to suppress output.
     * @param item The item to add.
     * @param number The amount of items to add.
     */
    public boolean addItem(Item item, int number, boolean silent) {
        if (item == null) {
            return false;
        }
        
        int oldGold = getGold();
        try {
            return i.addItem(item, number, silent);
        } finally {
            if (item instanceof GoldCoin && propertyChangeSupport != null) {
                propertyChangeSupport
                    .firePropertyChange(PROPERTY_GOLD, oldGold, getGold());
            }
        }
    }
    
    /**
     * Remove <var>number</var> <var>item</var>s from inventory.
     * @param item The item to remove.
     * @param number The amount of items to remove.
     * @return true on success, false otherwise.
     */
    public boolean removeItem(Item item, int number) {
        return removeItem(item, number, false);
    }
    
    /**
     * Remove <var>number</var> <var>item</var>s from inventory.
     * @return true on success, false otherwise.
     * @param silent True to suppress output.
     * @param item The item to remove.
     * @param number The amount of items to remove.
     */
    public boolean removeItem(Item item, int number, boolean silent) {
        if (item == null) {
            return false;
        }
        if (item instanceof GoldCoin) {
            int oldGold = getGold();
            if(number > oldGold) {
                return false;
            }
            if (propertyChangeSupport != null) {
                propertyChangeSupport
                    .firePropertyChange(PROPERTY_GOLD, oldGold,
                                        oldGold - number);
            }
        }
        return i.removeItem(item, number, silent);
    }
    
    /**
     * @return hp left after damage is done
     */
    public int damage(int amount) {
        int oldHp = getHp();
        int newHp = super.damage(amount);
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_HP, oldHp, newHp);
        }
        //if damage is done to Hero, DEFENSE goes up 10% of the time
        if(Control.random(0, 100) <= 10){
            addSkill(Skill.DEFENSE, 0.1);
        }
        return newHp;
    }
    
    public void heal(int amount) {
        int oldHp = getHp();
        super.heal(amount);
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_HP, oldHp, getHp());
        }
    }
    
    public void setHp(int hp) {
        int oldHp = getHp();
        super.setHp(hp);
        if (propertyChangeSupport != null) {
            propertyChangeSupport
                .firePropertyChange(PROPERTY_HP, oldHp, getHp());
        }
    }
    
    public int getAc() {
        return super.getAc() + getArmorAc();
    }
    
    public int getArmorAc() {
        return wornArmor.getTotalAc();
    }
    
    public int getWc() {
        int mod = 0;
        if (weapon != null) {
            mod = weapon.getWc();
        }
        return super.getWc() + mod;
    }
    /**
     *@return attack value, the higher the more likely to hit
     **/
    public int getAttack() {
        int attack = super.getAttack();
        int aSkill = (int)skillValue(Skill.ATTACK);
        return attack + aSkill;
    }
    
    /**
     * All damage taken is reduced by 0-resist
     *
     *@return resistance to specified damage type
     **/
    public int getResist(int damageType) {
        
        //Default:  10% of AC resist damage
        int resist = super.getResist(damageType);
        // 20% of defense Skill resist damage
        resist += (int)(skillValue(Skill.DEFENSE) / 5.0);
        
        return resist;
    }
    
    public void setBirthDate(long date) {
        birthDate = date;
    }
    
    public long getBirthDate() {
        return birthDate;
    }
    
    public QuestList getQuestList() {
        QuestList quests = new QuestList();
        Guild guild = HeroLocation.getHeroLocation()
            .getIslandMap().getTownMap().getGuild();
        Quest quest = guild.getQuest(this);
        if (quest != null) {
            quests.addQuest(quest);
        }
        return quests;
    }
    
    public void randomEquip(int level) {
        addItem(saga.model.items.LongSword.getLongSword(
        saga.model.items.LongSword.SHABBY_SWORD), 1);
        Armor a = Armor.getChest(Armor.RED_ROBE, level);
        addItem(a, 1);
        addItem(Armor.getCloak(Armor.BROWN_CLOAK, level), 1);
        addItem(Armor.getBoots(Armor.WORN_LEATHER_BOOTS, level), 1);
        addItem(Armor.getGloves(Armor.WORN_LEATHER_GLOVES, level), 1);
        addItem(Armor.getHelm(Armor.WORN_LEATHER_HELM, level), 1);
        addItem(Armor.getShield(Armor.ORC_SHIELD, level), 1);
        addItem(new saga.model.items.GoldCoin(), 100 * level);
    }
    
    /** Getter for property actionPoints.
     * @return Value of property actionPoints.
     */
    public int getActionPoints() {
        int actionPoints = super.getActionPoints();
        int maxWeight = getMaxWeight();
        int weight = (int)Math.ceil(getInventory().getWeight());
        if (weight > maxWeight) {
            weight -= maxWeight;
            if (weight < maxWeight) {
                actionPoints -= actionPoints * weight / maxWeight;
            } else {
                actionPoints = 0; // duh
            }
        }
        return actionPoints;
    }
    
    /** Setter for property speed.
     * @param speed New value of property speed.
     */
    public void setSpeed(int speed) {
        int oldAp = getActionPoints();
        super.setSpeed(speed);
        if (propertyChangeSupport != null) {
            propertyChangeSupport.firePropertyChange
            (PROPERTY_AP, oldAp, getActionPoints());
        }
    }
    
    /** Getter for property maxWeight.
     * @return Value of property maxWeight.
     */
    public int getMaxWeight() {
        return getStr() * 10;
    }
}
