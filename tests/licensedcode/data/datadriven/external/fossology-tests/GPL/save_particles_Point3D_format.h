/*
   This file belongs to Aeneas. Aeneas is a GNU package released under GPL 3 license.
   This code is a simulator for Submicron 3D Semiconductor Devices. 
   It implements the Monte Carlo transport in 3D tetrahedra meshes
   for the simulation of the semiclassical Boltzmann equation for both electrons.
   It also includes all the relevant quantum effects for nanodevices.

   Copyright (C) 2007 Jean Michel Sellier <sellier@dmi.unict.it>
 
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

// Created on : 17 june 2007, Siracusa, Jean Michel Sellier
// Last modified : 16 august 2007, Siracusa, Jean Michel Sellier

// save the position of all particles in Point3D format

// this is the format :
// # variable_name x y z
// v(1)      x(1)      y(1)      z(1)
// v(2)      x(2)      y(2)      z(2)
// ...
// v(i)      x(i)      y(i)      z(i)
// ...
// v(INUM-1) x(INUM-1) y(INUM-1) z(INUM-1)
// v(INUM)   x(INUM)   y(INUM)   z(INUM)

void save_particles_Point3D_format(int num)
{
 int i,n;
 FILE *fp1, *fp2, *fp3;
 char s1[180], s2[180], s3[180];

 sprintf(s1,"particles/energy_Point3D_format/particles_ener%d.3d",num);
 if(num<100) sprintf(s1,"particles/energy_Point3D_format/particles_ener0%d.3d",num); 
 if(num<10)  sprintf(s1,"particles/energy_Point3D_format/particles_ener00%d.3d",num);

 sprintf(s2,"particles/potential_Point3D_format/particles_pot%d.3d",num);
 if(num<100) sprintf(s2,"particles/potential_Point3D_format/particles_pot0%d.3d",num);
 if(num<10)  sprintf(s2,"particles/potential_Point3D_format/particles_pot00%d.3d",num);

 sprintf(s3,"particles/position_Point3D_format/particles_pos%d.3d",num);
 if(num<100) sprintf(s3,"particles/position_Point3D_format/particles_pos0%d.3d",num);
 if(num<10)  sprintf(s3,"particles/position_Point3D_format/particles_pos00%d.3d",num);

 printf("Saving %d particles datas in Point3D format... num = %d\n",INUM,num);

 fp1=fopen(s1,"w"); 
 if(fp1==NULL){
    printf("save_particles_Point3D : impossible to open the fp1 output file!\n");
    system("PAUSE");
    exit(0);
 }
 fp2=fopen(s2,"w");
 if(fp2==NULL){
    printf("save_particles_Point3D : impossible to open the fp2 output file!\n");
    system("PAUSE");
    exit(0);
 }
 fp3=fopen(s3,"w");
 if(fp3==NULL){
    printf("save_particles_Point3D : impossible to open the fp3 output file!\n");
    system("PAUSE");
    exit(0);
 }

 fprintf(fp1,"# x y z energy\n");
 fprintf(fp2,"# x y z potential\n");
 fprintf(fp3,"# x y z nomeaning\n");

// printf("INUM = %d\n",INUM);
 
 for(n=1;n<=INUM;n++){
//        printf("n = %d\n",n);
   int iv;
   double x,y,z;
   double energy=0., potential;
   double thesquareroot, ksquared;
   iv=(int) P[n][0];
   i=(int) P[n][9];
   x=0.25*(P[n][5]*coord[0][noeud_geo[0][i]-1]
          +P[n][6]*coord[0][noeud_geo[1][i]-1]
          +P[n][7]*coord[0][noeud_geo[2][i]-1]
          +P[n][8]*coord[0][noeud_geo[3][i]-1]);
   y=0.25*(P[n][5]*coord[1][noeud_geo[0][i]-1]
          +P[n][6]*coord[1][noeud_geo[1][i]-1]
          +P[n][7]*coord[1][noeud_geo[2][i]-1]
          +P[n][8]*coord[1][noeud_geo[3][i]-1]);
   z=0.25*(P[n][5]*coord[2][noeud_geo[0][i]-1]
          +P[n][6]*coord[2][noeud_geo[1][i]-1]
          +P[n][7]*coord[2][noeud_geo[2][i]-1]
          +P[n][8]*coord[2][noeud_geo[3][i]-1]);
   potential=0.25*(V[noeud_geo[0][i]-1]+V[noeud_geo[1][i]-1]+
                   V[noeud_geo[2][i]-1]+V[noeud_geo[3][i]-1]);
   ksquared=P[n][1]*P[n][1]+P[n][2]*P[n][2]+P[n][3]*P[n][3];
   if(i_dom[i]!=SIO2){
     thesquareroot=sqrt(1.+4.*alphaK[i_dom[i]][iv]*HHM[i_dom[i]][iv]*ksquared);
     energy=(thesquareroot-1.)/(2.*alphaK[i_dom[i]][iv]);
   }
   fprintf(fp1,"%f %f %f %g\n",x*1.e6,y*1.e6,z*1.e6,energy);
   fprintf(fp2,"%f %f %f %g\n",x*1.e6,y*1.e6,z*1.e6,potential);
   fprintf(fp3,"%f %f %f  1\n",x*1.e6,y*1.e6,z*1.e6);
 }
 fclose(fp1);    
 fclose(fp2);
 fclose(fp3);
}
