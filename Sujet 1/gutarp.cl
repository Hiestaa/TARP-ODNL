__kernel void gutarp(__global int* baseTab, __global int* idTab, int hauteur, int largeur, __global int* result)
{	
	int id = get_global_id(0);
	
	int resultTab[hauteur * largeur];
	
	result[0] = baseTab[idTab[0]];
	
	int i = 1;
	while (i < hauteur)
	{
		resultTab[i * largeur] = baseTab[(i - 1) * largeur + idTab[0 + id * largeur]] + baseTab[i * largeur + idTab[0+ id * largeur]];
		i += 1;
	}
	
	int j = 1;
	int tmp = 0;
	while (j < largeur)
	{
		resultTab[j] = baseTab[idTab[j - 1 + id * largeur]] + baseTab[idTab[j + id * largeur]] ;
		i = 1
		while (i < hauteur)
		{
			if (resultTab[j - 1 + i * largeur] > resultTab[j + (i - 1) * largeur])
				tmp = resultTab[j - 1 + i * largeur];
			else
				tmp = resultTab[j + (i - 1) * largeur];
			resultTab[j + i * largeur] = baseTab[idTab[j + id * largeur] + i * largeur] + tmp;
			i += 1;
		}
		j += 1;
	}
	result[id] = resultTab[largeur - 1 + (hauteur - 1) * largeur]
}